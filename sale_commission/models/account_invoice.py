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
    @api.depends('invoice_line.commissions.amount')
    def _get_commission_total(self):
        self.commission_total = 0.0
        for line in self.invoice_line:
            self.commission_total += sum(x.amount for x in line.commissions)
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
    """Invoice Line inherit to add commissions"""
    _inherit = "account.invoice.line"

    @api.model
    def _default_commissions(self):
        res = self.env['sale.commission'].get_default_commissions()
        return [(0, 0, x) for x in res]

    commissions = fields.One2many(
        comodel_name="account.invoice.line.commission",
        inverse_name="invoice_line", string="Agents & commissions",
        help="Agents/Commissions related to the invoice line.",
        default=_default_commissions, copy=True)
    commission_free = fields.Boolean(
        string="Comm. free", related="product_id.commission_free",
        store=True, readonly=True)


class AccountInvoiceLineAgentCommission(models.Model):
    _name = "account.invoice.line.commission"
    _description = "Commissions to be paid on an invoice line"

    invoice_line = fields.Many2one(
        comodel_name="account.invoice.line", required=True, ondelete="cascade")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")
    agent = fields.Many2one(
        comodel_name="res.partner", required=True, ondelete="restrict",
        domain="[('agent', '=', True)]")

    invoice = fields.Many2one(
        comodel_name="account.invoice", string="Invoice",
        related="invoice_line.invoice_id", store=True)
    invoice_date = fields.Date(
        string="Invoice date", related="invoice.date_invoice", store=True,
        readonly=True)
    product = fields.Many2one(
        comodel_name='product.product', related="invoice_line.product_id")
    amount = fields.Float(
        string="Amount settled", compute="_get_amount", store=True)
    settled = fields.Boolean(compute="_get_settled", store=True)
    settlement_id = fields.Many2one("sale.commission.settlement")

    @api.one
    @api.depends('commission.commission_type', 'invoice_line.price_subtotal')
    def _get_amount(self):
        self.amount = 0.0
        if self.commission:
            self.amount = self.commission.compute_invoice_commission(
                self.invoice_line)

    @api.one
    @api.depends('settlement_id', 'settlement_id.state',
                 'invoice', 'invoice.state')
    def _get_settled(self):
        # Count as settled if either:
        # - our invoice isn't open or paid (nothing to settle)
        # - we have a settled or invoiced settlement
        self.settled = bool(
            self.invoice.state not in ('open', 'paid') or
            self.settlement_id and
            self.settlement_id.state in ('settled', 'invoiced')
        )

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(invoice_line, agent, commission)',
         'You can only add one time per commission per agent.')
    ]
