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

    def _get_line_uom(self):
        return self.object_id.product_uom_id

    def _get_commission_currency(self):
        return self.object_id.currency_id

    def _get_commission_date(self):
        order = self.object_id.order_id
        if not order.date_order:
            return super()._get_commission_date()
        return self._get_company_date(order.date_order)

    @api.depends(
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_uom_qty",
        "object_id.product_uom_id",
        "object_id.currency_id",
        "object_id.order_id.date_order",
    )
    def _compute_amount(self):  # pylint: disable=W8110 # Computes don't return
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
                super(SaleOrderLineAgent, line)._compute_amount()
