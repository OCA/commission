# -*- coding: utf-8 -*-
# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    """Invoice inherit to add salesman"""
    _inherit = "account.invoice"

    @api.depends('invoice_line_ids.agents.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.invoice_line_ids:
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

    @api.multi
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

    @api.model
    def _prepare_line_agents_data(self, line):
        rec = []
        for agent in self.partner_id.agents:
            rec.append({
                'agent': agent.id,
                'commission': agent.commission.id,
            })
        return rec

    @api.multi
    def recompute_lines_agents(self):
        for invoice in self:
            for line in invoice.invoice_line_ids:
                line.agents.unlink()
                line_agents_data = invoice._prepare_line_agents_data(line)
                line.agents = [(
                    0,
                    0,
                    line_agent_data) for line_agent_data in line_agents_data]


class AccountInvoiceLine(models.Model):
    _inherit = [
        "account.invoice.line",
        "sale.commission.mixin",
    ]
    _name = "account.invoice.line"

    agents = fields.One2many(
        comodel_name="account.invoice.line.agent",
    )


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
    product = fields.Many2one(
        comodel_name='product.product',
        related="object_id.product_id",
    )
    amount = fields.Float(
        string="Amount settled",
        compute="_compute_amount",
        store=True,
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
        store=True, copy=False)

    @api.depends('object_id.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            if (not line.object_id.commission_free and
                    line.commission):
                if line.commission.amount_base_type == 'net_amount':
                    subtotal = (line.object_id.price_subtotal -
                                (line.product.standard_price *
                                 line.object_id.quantity))
                else:
                    subtotal = line.object_id.price_subtotal
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
