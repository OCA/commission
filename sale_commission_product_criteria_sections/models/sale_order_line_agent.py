# Copyright 2025 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        # It is defined on the models and not on the mixin because other
        # modules of the product criteria family replace it on the models.
        commission_item = self._get_section_commission_item(commission, product)
        if commission_item:
            return self._get_section_commission_amount(
                commission_item, commission, subtotal, product, quantity
            )
        return super()._get_single_commission_amount(
            commission, subtotal, product, quantity
        )
