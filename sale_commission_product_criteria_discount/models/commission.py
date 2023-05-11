# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

COMMISSION_ITEM_TYPES = {
    "0_product_variant": 1000,
    "1_product": 10000,
    "2_product_category": 100000,
    "3_global": 1000000,
}


class CommissionItem(models.Model):
    _inherit = "commission.item"

    based_on = fields.Selection(
        selection_add=[("discount", "Discount")],
        ondelete={"discount": "set default"},
    )
    discount_from = fields.Float("Discount From")
    discount_to = fields.Float("Discount To")

    @api.constrains("discount_from", "discount_to")
    def _check_discounts(self):
        if any(item.discount_from > item.discount_to for item in self):
            raise ValidationError(
                _("Discount From should be lower than the Discount To.")
            )
        return True


class SaleCommission(models.Model):
    _inherit = "sale.commission"

    def sort_items(self):
        # Priority 1: product_variant > product > product_category > global
        # Priority 2 (inside of priority 1):
        # Discount > SOL
        # Priority 3 (inside of priority 2):
        # Regular with price list > Regular without price list
        for com_type, seq in COMMISSION_ITEM_TYPES.items():
            all_lines = self.item_ids.filtered(lambda x: x.applied_on == com_type)
            sol_lines = all_lines.filtered(lambda x: x.based_on == "sol")
            disc_lines = all_lines.filtered(lambda x: x.based_on == "discount")
            disc_lines.update({"sequence": seq + 10})
            sol_lines.update({"sequence": seq + 100})
