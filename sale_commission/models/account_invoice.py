# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.depends('invoice_line_ids.agents.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.invoice_line_ids:
                record.commission_total += sum(x.amount for x in line.agents)

    commission_total = fields.Float(
        string="Commissions",
        compute="_compute_commission_total",
        store=True,
    )

    def action_cancel(self):
        """Put settlements associated to the invoices in exception."""
        settlements = self.env['sale.commission.settlement'].search(
            [('invoice', 'in', self.ids)])
        settlements.write({'state': 'except_invoice'})
        return super(AccountInvoice, self).action_cancel()

    def invoice_validate(self):
        """Put settlements associated to the invoices in invoiced state."""
        self.env['sale.commission.settlement'].search(
            [('invoice', 'in', self.ids)]
        ).write({'state': 'invoiced'})
        return super(AccountInvoice, self).invoice_validate()

    def _refund_cleanup_lines(self, lines):
        """ugly function to map all fields of account.invoice.line
        when creates refund invoice"""
        res = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        if lines and lines[0]._name != 'account.invoice.line':
            return res
        for i, line in enumerate(lines):
            vals = res[i][2]
            agents = super(AccountInvoice, self)._refund_cleanup_lines(
                line['agents'])
            # Remove old reference to source invoice
            for agent in agents:
                agent_vals = agent[2]
                del agent_vals['invoice']
                del agent_vals['object_id']
            vals['agents'] = agents
        return res

    def recompute_lines_agents(self):
        self.mapped('invoice_line_ids').recompute_agents()


class AccountInvoiceLine(models.Model):
    _inherit = [
        "account.invoice.line",
        "sale.commission.mixin",
    ]
    _name = "account.invoice.line"

    agents = fields.One2many(
        comodel_name="account.invoice.line.agent",
    )
    any_settled = fields.Boolean(
        compute="_compute_any_settled",
    )

    @api.depends('agents', 'agents.settled')
    def _compute_any_settled(self):
        for record in self:
            record.any_settled = any(record.mapped('agents.settled'))

    @api.model
    def create(self, vals):
        """Add agents for records created from automations instead of UI."""
        # We use this form as this is the way it's returned when no real vals
        agents_vals = vals.get('agents', [(6, 0, [])])
        invoice_id = vals.get('invoice_id', False)
        if (agents_vals and agents_vals[0][0] == 6 and not
                agents_vals[0][2] and invoice_id):
            vals['agents'] = self._prepare_agents_vals(vals=vals)
        return super().create(vals)

    def _prepare_agents_vals(self, vals=None):
        res = super()._prepare_agents_vals(vals=vals)
        if self:
            partner = self.invoice_id.partner_id
        else:
            invoice = self.env['account.invoice'].browse(vals['invoice_id'])
            partner = invoice.partner_id
        return res + self._prepare_agents_vals_partner(partner)


class AccountInvoiceLineAgent(models.Model):
    _inherit = "sale.commission.line.mixin"
    _name = "account.invoice.line.agent"

    object_id = fields.Many2one(
        comodel_name="account.invoice.line",
        oldname='invoice_line',
    )
    invoice = fields.Many2one(
        string="Invoice",
        comodel_name="account.invoice",
        related="object_id.invoice_id",
        store=True,
    )
    invoice_date = fields.Date(
        string="Invoice date",
        related="invoice.date_invoice",
        store=True,
        readonly=True,
    )
    agent_line = fields.Many2many(
        comodel_name='sale.commission.settlement.line',
        relation='settlement_agent_line_rel',
        column1='agent_line_id',
        column2='settlement_id',
        copy=False,
    )
    settled = fields.Boolean(
        compute="_compute_settled",
        store=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        compute="_compute_company",
        store=True,
    )
    currency_id = fields.Many2one(
        related="object_id.currency_id",
        readonly=True,
    )

    @api.depends('object_id.price_subtotal')
    def _compute_amount(self):
        for line in self:
            inv_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission, inv_line.price_subtotal,
                inv_line.product_id, inv_line.quantity,
            )
            # Refunds commissions are negative
            if 'refund' in line.invoice.type:
                line.amount = -line.amount

    @api.depends('agent_line', 'agent_line.settlement.state', 'invoice',
                 'invoice.state')
    def _compute_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        for line in self:
            line.settled = (any(x.settlement.state != 'cancel'
                                for x in line.agent_line))

    @api.depends('object_id', 'object_id.company_id')
    def _compute_company(self):
        for line in self:
            line.company_id = line.object_id.company_id

    @api.constrains('agent', 'amount')
    def _check_settle_integrity(self):
        for record in self:
            if any(record.mapped('settled')):
                raise exceptions.ValidationError(
                    _("You can't modify a settled line"),
                )

    def _skip_settlement(self):
        """This function should return if the commission can be payed.

        :return: bool
        """
        self.ensure_one()
        return (
            self.commission.invoice_state == 'paid' and
            self.invoice.state != 'paid'
        ) or (self.invoice.state not in ('open', 'paid'))
