# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2020 ElvenStudio - Vincenzo Terzulli <v.terzulli@elvenstudio.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def get_commission_from_pricelist(self):
        self.ensure_one()
        res = False
        if self.product_id and self.order_id.pricelist_id:
            pr_dict = self.order_id.pricelist_id.price_rule_get_multi(
                products_by_qty_by_partner=[(self.product_id,
                                             self.product_uom_qty or 1.0,
                                             self.order_id.partner_id)])
            rule = pr_dict[self.product_id.id][self.order_id.pricelist_id.id][1]
            rule_id = self.env['product.pricelist.item'].browse(rule)
            res = rule_id.commission_id
        return res

    @api.one
    @api.onchange('product_id', 'product_uom_qty')
    def onchange_product_id_sale_commission_pricelist(self):
        commission = self.get_commission_from_pricelist()
        if commission:
            for agent in self.agents:
                agent.update({
                    'commission': commission.id,
                })
