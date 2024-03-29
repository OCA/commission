#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    def _get_discount_value(self, commission_item):
        sale_line = self.object_id
        if commission_item.used_discount == "first":
            discount_value = sale_line.discount
        elif commission_item.used_discount == "computed":
            discount_value = sale_line._get_final_discount()
        else:
            discount_value = super()._get_discount_value(commission_item)
        return discount_value
