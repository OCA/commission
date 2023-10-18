# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    discount = fields.Float(related="object_id.discount")
    applied_commission_item_id = fields.Many2one("commission.item")
    based_on = fields.Selection(related="applied_commission_item_id.based_on")
    applied_on_name = fields.Char(related="applied_commission_item_id.name")
    commission_type = fields.Selection(
        related="applied_commission_item_id.commission_type"
    )
    fixed_amount = fields.Float(related="applied_commission_item_id.fixed_amount")
    percent_amount = fields.Float(related="applied_commission_item_id.percent_amount")

    @api.depends(
        "object_id.price_subtotal", "object_id.product_id", "object_id.product_uom_qty"
    )
    def _compute_amount(self):
        res = None
        for line in self:
            if line.commission_id and line.commission_id.commission_type == "product":
                order_line = line.object_id
                line.amount = line._get_single_commission_amount(
                    line.commission_id,
                    order_line.price_subtotal,
                    order_line.product_id,
                    order_line.product_uom_qty,
                )
            else:
                res = super(SaleOrderLineAgent, line)._compute_amount()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals["agent_ids"] = [
            (
                0,
                0,
                {
                    "agent_id": x.agent_id.id,
                    "commission_id": x.commission_id.id,
                },
            )
            for x in self.agent_ids
        ]
        return vals
