from odoo import models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        self.ensure_one()
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return 0.0
        commission_item = self.env["commission.item"].browse(item_ids[0])
        if commission.amount_base_type == "net_amount":
            subtotal = max([0, subtotal - product.standard_price * quantity])
        self.applied_commission_item_id = commission_item
        self.applied_commission_id = commission_item.commission_id
        if commission_item.commission_type == "fixed":
            return commission_item.fixed_amount
        elif commission_item.commission_type == "percentage":
            return subtotal * (commission_item.percent_amount / 100.0)
        elif commission_item.commission_type == "section":
            return commission_item._calculate_section_amount(subtotal)
