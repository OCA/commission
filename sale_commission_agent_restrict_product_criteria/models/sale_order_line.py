from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_domain_ids = fields.Many2many(related="order_id.product_domain_ids")
