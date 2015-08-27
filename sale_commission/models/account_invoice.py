# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#    Copyright (C) 2015 Avanzosc (<http://www.avanzosc.es>)
#    Copyright (C) 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    """Invoice inherit to add salesman"""
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line.agents.amount')
    def _get_commission_total(self):
        self.commission_total = 0.0
        for line in self.invoice_line:
            self.commission_total += sum(x.amount for x in line.agents)
        # Consider also purchase refunds, although not in the initial scope
        if self.type in ('out_refund', 'in_refund'):
            self.commission_total = -self.commission_total

    commission_total = fields.Float(
        string="Commissions", compute="_get_commission_total",
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
        for line in res:
            if 'commission_ids' in line[2]:
                commission_ids = [(6, 0, line[2]['commission_ids'])]
                line[2]['commission_ids'] = commission_ids
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
                agents.append({'agent': agent.id,
                               'commission': agent.commission.id})
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
        comodel_name="account.invoice.line", required=True, ondelete="cascade")
    invoice = fields.Many2one(
        comodel_name="account.invoice", string="Invoice",
        related="invoice_line.invoice_id", store=True)
    invoice_date = fields.Date(
        string="Invoice date", related="invoice.date_invoice", store=True,
        readonly=True)
    product = fields.Many2one(
        comodel_name='product.product', related="invoice_line.product_id")
    agent = fields.Many2one(
        comodel_name="res.partner", required=True, ondelete="restrict",
        domain="[('agent', '=', True)]")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")
    amount = fields.Float(
        string="Amount settled", compute="_get_amount", store=True)
    agent_line = fields.Many2many(
        comodel_name='sale.commission.settlement.line',
        relation='settlement_agent_line_rel', column1='agent_line_id',
        column2='settlement_id')
    settled = fields.Boolean(compute="_get_settled", store=True)

    @api.one
    @api.onchange('agent')
    def onchange_agent(self):
        self.commission = self.agent.commission

    @api.one
    @api.depends('commission.commission_type', 'invoice_line.price_subtotal')
    def _get_amount(self):
        self.amount = 0.0
        sign = {
            'out_invoice': 1, 'in_invoice': -1,
            'out_refund': -1, 'in_refund': 1,
        }[self.invoice.type or 'out_invoice']
        amount = self.commission.compute_invoice_commission(
            self.invoice_line)
        self.amount = sign * amount

    @api.one
    @api.depends('agent_line', 'agent_line.settlement.state', 'invoice',
                 'invoice.state')
    def _get_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        self.settled = (self.invoice.state not in ('open', 'paid') or
                        any(x.settlement.state != 'cancel'
                            for x in self.agent_line))

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(invoice_line, agent)',
         'You can only add one time each agent.')
    ]
