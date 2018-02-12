# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_sale_commission_pricelist(self):
        self.ensure_one()
        if self.product_id and self.order_id.pricelist_id:
            rule_id = self.order_id.pricelist_id.get_product_price_rule(
                product=self.product_id,
                quantity=self.product_uom_qty or 1.0,
                partner=self.order_id.partner_id,
                date=self.order_id.date_order,
                uom_id=self.product_uom.id)[1]
            rule = self.env['product.pricelist.item'].browse(rule_id)
            if rule.commission_id:
                self.agents.update({
                    'commission': rule.commission_id.id,
                })
