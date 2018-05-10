# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends('sale_line.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            if (not line.sale_line.product_id.commission_free and
                line.commission) and \
                    line.commission.commission_type == 'brand':
                price_subtotal = line.sale_line.price_subtotal
                standard_price = line.sale_line.product_id.standard_price
                qty = line.sale_line.product_uom_qty
                for brand in line.commission.brand_lines:
                    if line.sale_line.product_id.product_brand_id == \
                            brand.brand_id:
                        if line.commission.amount_base_type == 'net_amount':
                            subtotal = (price_subtotal -
                                        (standard_price * qty))
                        else:
                            subtotal = line.sale_line.price_subtotal
                        line.amount = subtotal * (brand.percent / 100.0)
            else:
                super(SaleOrderLineAgent, self)._compute_amount()
