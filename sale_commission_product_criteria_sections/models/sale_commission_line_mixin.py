# Copyright 2025 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _get_commission_base_amount(self, commission, subtotal, product, quantity):
        """Return the base amount used to compute the commission of the line.

        It is the amount of the line, without the cost of the product when the
        base of the commission is the margin. The base implementation does not
        expose it, so it is computed here.
        """
        self.ensure_one()
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        return subtotal
