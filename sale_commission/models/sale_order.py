# -*- coding: utf-8 -*-
# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
        for order in self:
            for line in order.order_line:
                line.agents.unlink()
                line_agents_data = order._prepare_line_agents_data(line)
                line.agents = [(
                    0,
                    0,
                    line_agent_data) for line_agent_data in line_agents_data]


class SaleOrderLine(models.Model):
    _inherit = [
        "sale.order.line",
        "sale.commission.mixin",
    ]
    _name = "sale.order.line"

    agents = fields.One2many(
        comodel_name="sale.order.line.agent",
    )

    @api.multi
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
            line.amount = 0.0
            if (not line.object_id.product_id.commission_free and
                    line.commission):
                if line.commission.amount_base_type == 'net_amount':
                    subtotal = (line.object_id.price_subtotal -
                                (line.object_id.product_id.standard_price *
                                 line.object_id.product_uom_qty))
                else:
                    subtotal = line.object_id.price_subtotal
                if line.commission.commission_type == 'fixed':
                    line.amount = subtotal * (line.commission.fix_qty / 100.0)
                else:
                    line.amount = line.commission.calculate_section(subtotal)
