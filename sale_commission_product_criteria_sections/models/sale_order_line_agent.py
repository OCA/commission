# Copyright 2025 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        # It is defined on the models and not on the mixin because other
        # modules of the product criteria family replace it on the models.
        # The base implementation resolves the commission items and applies
        # the first one, but it does not know the section type, so the amount
        # of the applied commission item is computed here when it defines
        # sections. The commission items are resolved only once by the base
        # implementation.
        amount = super()._get_single_commission_amount(
            commission, subtotal, product, quantity
        )
        if amount is not None:
            return amount
        commission_item = self.applied_commission_item_id
        if commission_item.commission_type != "section":
            return amount
        return commission_item._calculate_section_amount(
            self._get_commission_base_amount(
                commission, subtotal, product, quantity
            )
        )
