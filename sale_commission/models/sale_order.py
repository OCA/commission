# -*- coding: utf-8 -*-
# Copyright 2014-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from lxml import etree


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.agents.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.order_line:
                record.commission_total += sum(x.amount for x in line.agents)

    commission_total = fields.Float(
        string="Commissions", compute="_compute_commission_total",
        store=True)

    def recompute_lines_agents(self):
        self.mapped('order_line').recompute_agents()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Add to the existing context of the field `order_line` "partner_id"
        key for avoiding to be replaced by other view inheritance.

        We have to do this processing in text mode without evaling context, as
        it can contain JS stuff.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='order_line']"):
                node_val = node.get('context', '{}').strip()[1:-1]
                elems = node_val.split(',') if node_val else []
                to_add = ["'partner_id': partner_id"]
                node.set('context', '{' + ', '.join(elems + to_add) + '}')
            res['arch'] = etree.tostring(doc)
        return res


class SaleOrderLine(models.Model):
    _inherit = [
        "sale.order.line",
        "sale.commission.mixin",
    ]
    _name = "sale.order.line"

    agents = fields.One2many(
        comodel_name="sale.order.line.agent",
    )

    def _prepare_agents_vals(self):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_agents_vals()
        for agent in self.order_id.partner_id.agents:
            res.append({
                'agent': agent.id,
                'commission': agent.commission.id,
            })
        return res

    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        vals['agents'] = [
            (0, 0, {'agent': x.agent.id,
                    'commission': x.commission.id}) for x in self.agents]
        return vals


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.commission.line.mixin"
    _name = "sale.order.line.agent"
    _rec_name = "agent"

    object_id = fields.Many2one(
        comodel_name="sale.order.line",
        oldname='sale_line',
    )
    amount = fields.Float(compute="_compute_amount", store=True)

    @api.depends('object_id.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = line._get_commission_amount(
                line.commission,
                line.object_id.price_subtotal,
                line.object_id.product_id.commission_free,
                line.object_id.product_id,
                line.object_id.product_uom_qty)
