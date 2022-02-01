from odoo import fields, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    discount_from = fields.Float(related="applied_commission_item_id.discount_from")
    discount_to = fields.Float(related="applied_commission_item_id.discount_to")
