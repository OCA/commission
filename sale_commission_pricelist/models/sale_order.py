# Copyright 2018 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_commission_from_pricelist(self):
        self.ensure_one()
        if not self.product_id or not self.order_id.pricelist_id:
            return False    # pragma: no cover
        rule_id = self.order_id.pricelist_id.get_product_price_rule(
            product=self.product_id,
            quantity=self.product_uom_qty or 1.0,
            partner=self.order_id.partner_id,
            date=self.order_id.date_order,
            uom_id=self.product_uom.id)[1]
        rule = self.env['product.pricelist.item'].browse(rule_id)
        return rule.commission_id

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_sale_commission_pricelist(self):
        commission = self._get_commission_from_pricelist()
        if commission:
            self.agents.update({
                'commission': commission.id,
            })

    def _prepare_agents_vals(self, vals=None):
        res = super()._prepare_agents_vals(vals=vals)
        commission = self._get_commission_from_pricelist() if self else False
        if commission:
            for vals in res:
                vals[2]['commission'] = commission.id
        return res
