# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# © 2016 Andrea Cometa (<http://www.apuliasoftware.it>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    """Invoice inherit to add salesman"""
    _inherit = "account.invoice"

    @api.depends('invoice_line.agents.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.invoice_line:
                record.commission_total += sum(x.amount for x in line.agents)

    commission_total = fields.Float(
        string="Commissions", compute="_compute_commission_total",
        store=True)

    @api.multi
    def action_cancel(self):
        """Put settlements associated to the invoices in exception."""
        settlements = self.env['sale.commission.settlement'].search(
            [('invoice', 'in', self.ids)])
        settlements.write({'state': 'except_invoice'})
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def invoice_validate(self):
        """Put settlements associated to the invoices again in invoice."""
        settlements = self.env['sale.commission.settlement'].search(
            [('invoice', 'in', self.ids)])
        settlements.write({'state': 'invoiced'})
        return super(AccountInvoice, self).invoice_validate()

    @api.model
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
                del agent_vals['invoice_line']
            vals['agents'] = agents
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _default_agents(self):
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for agent in partner.agents:
                vals = {
                    'agent': agent.id,
                    'commission': agent.commission.id,
                }
                vals['display_name'] = self.env['account.invoice.line.agent']\
                    .new(vals).display_name
                agents.append(vals)
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(
        comodel_name="account.invoice.line.agent",
        inverse_name="invoice_line", string="Agents & commissions",
        help="Agents/Commissions related to the invoice line.",
        default=_default_agents, copy=True)
    commission_free = fields.Boolean(
        string="Comm. free", related="product_id.commission_free",
        store=True, readonly=True)


class AccountInvoiceLineAgent(models.Model):
    _name = "account.invoice.line.agent"

    invoice_line = fields.Many2one(
        comodel_name="account.invoice.line",
        ondelete="cascade",
        required=True, copy=False)
    invoice = fields.Many2one(
        string="Invoice", comodel_name="account.invoice",
        related="invoice_line.invoice_id",
        store=True)
    invoice_date = fields.Date(
        string="Invoice date",
        related="invoice.date_invoice",
        store=True, readonly=True)
    product = fields.Many2one(
        comodel_name='product.product',
        related="invoice_line.product_id")
    agent = fields.Many2one(
        comodel_name="res.partner",
        domain="[('agent', '=', True)]",
        ondelete="restrict",
        required=True)
    commission = fields.Many2one(
        comodel_name="sale.commission", ondelete="restrict", required=True)
    amount = fields.Float(
        string="Amount settled", compute="_compute_amount", store=True)
    agent_line = fields.Many2many(
        comodel_name='sale.commission.settlement.line',
        relation='settlement_agent_line_rel',
        column1='agent_line_id', column2='settlement_id',
        copy=False)
    settled = fields.Boolean(
        compute="_compute_settled",
        store=True, copy=False)
    company_id = fields.Many2one("res.company", "Company",
                                 related="invoice.company_id", store=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%s: %s" % (record.agent.name, record.commission.name)
            res.append((record.id, name))
        return res

    @api.depends('agent', 'commission')
    def _compute_display_name(self):
        return super(AccountInvoiceLineAgent, self)._compute_display_name()

    @api.onchange('agent')
    def onchange_agent(self):
        self.commission = self.agent.commission

    @api.depends('invoice_line.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            if (not line.invoice_line.product_id.commission_free and
                    line.commission):
                l = line.invoice_line
                subtotal = l.invoice_line_tax_id.compute_all(
                    (l.price_unit * (1 - (l.discount or 0.0) / 100.0)),
                    l.quantity, l.product_id, line.invoice.partner_id)
                if line.commission.amount_base_type == 'net_amount':
                    subtotal = subtotal['total']
                else:
                    subtotal = subtotal['total_included']
                if line.commission.commission_type == 'fixed':
                    line.amount = subtotal * (line.commission.fix_qty / 100.0)
                else:
                    line.amount = line.commission.calculate_section(subtotal)
                # Refunds commissions are negative
                if line.invoice.type in ('out_refund', 'in_refund'):
                    line.amount = -line.amount

    @api.depends('agent_line', 'agent_line.settlement.state', 'invoice',
                 'invoice.state')
    def _compute_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        for line in self:
            line.settled = (line.invoice.state not in ('open', 'paid') or
                            any(x.settlement.state != 'cancel'
                                for x in line.agent_line))

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(invoice_line, agent)',
         'You can only add one time each agent.')
    ]
