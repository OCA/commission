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


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    @api.depends('order_line.commissions.amount')
    def _get_commission_total(self):
        self.commission_total = 0.0
        for line in self.order_line:
            self.commission_total += sum(x.amount for x in line.commissions)

    commission_total = fields.Float(
        string="Commissions", compute="_get_commission_total",
        store=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_commissions(self):
        res = self.env['sale.commission'].get_default_commissions()
        return [(0, 0, x) for x in res]

    commissions = fields.One2many(
        string="Agents & commissions",
        comodel_name='sale.order.line.commission', inverse_name='sale_line',
        copy=True, default=_default_commissions)
    commission_free = fields.Boolean(
        string="Comm. free", related="product_id.commission_free",
        store=True, readonly=True)

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id=account_id)
        vals['commissions'] = [
            (0, 0, {'agent': c.agent.id,
                    'commission': c.commission.id})
            for c in line.commissions]
        return vals


class SaleOrderLineCommission(models.Model):
    _name = "sale.order.line.commission"
    _rec_name = "agent"

    sale_line = fields.Many2one(
        comodel_name="sale.order.line", required=True, ondelete="cascade")
    agent = fields.Many2one(
        comodel_name="res.partner", required=True, ondelete="restrict",
        domain="[('agent', '=', True')]")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")
    amount = fields.Float(compute="_get_amount", store=True)

    _sql_constraints = [
        ('unique_agent_commission', 'UNIQUE(sale_line, agent, commission)',
         'You can only add one of each commission for each agent.')
    ]

    @api.one
    @api.depends('commission.commission_type', 'sale_line.price_subtotal')
    def _get_amount(self):
        self.amount = 0.0
        if self.commission:
            self.amount = self.commission.compute_sale_commission(
                self.sale_line)
