# coding: utf-8
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        """ add agents to values dict when there is none """
        values = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty)
        order = self.sudo().browse(order_id)
        order_line = order._cart_find_product_line(product_id)
        if order_line and not order_line.agents:
            values['agents'] = [
                (0, 0, x) for x in order_line._prepare_agents_vals()]
        return values
