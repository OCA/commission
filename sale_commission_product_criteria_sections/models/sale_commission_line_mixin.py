# Copyright 2025 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _get_section_commission_item(self, commission, product):
        """Return the commission item to compute by sections, if any.

        The first item matching the product and the commission is the one
        applied, so the section type is only used when that item defines it.
        """
        self.ensure_one()
        # Items are fetched with a raw query on every line, so the section
        # type is looked for before resolving them.
        if not any(
            commission_item.commission_type == "section"
            for commission_item in commission.item_ids
        ):
            return self.env["commission.item"]
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return self.env["commission.item"]
        commission_item = self.env["commission.item"].browse(item_ids[0])
        if commission_item.commission_type != "section":
            return self.env["commission.item"]
        return commission_item

    def _get_section_commission_amount(
        self, commission_item, commission, subtotal, product, quantity
    ):
        """Return the amount of ``commission_item`` following its sections."""
        self.ensure_one()
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        self.applied_commission_item_id = commission_item
        self.applied_commission_id = commission_item.commission_id
        return commission_item._calculate_section_amount(subtotal)
