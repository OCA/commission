from odoo import api, fields, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    discount = fields.Float(related="object_id.discount")
    applied_commission_item_id = fields.Many2one('commission.item')
    applied_on_name = fields.Char(related="applied_commission_item_id.name")
    discount_from = fields.Float(related="applied_commission_item_id.discount_from")
    discount_to = fields.Float(related="applied_commission_item_id.discount_to")
    commission_type = fields.Selection(
        related="applied_commission_item_id.commission_type"
    )
    fixed_amount = fields.Float(related="applied_commission_item_id.fixed_amount")
    percent_amount = fields.Float(related="applied_commission_item_id.percent_amount")

    @api.depends(
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_uom_qty",
    )
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            line.amount, line.applied_commission_item_id = line._get_commission_amount(
                line.commission_id,
                order_line.price_subtotal,
                order_line.product_id,
                order_line.product_uom_qty,
                order_line.discount
            )
