# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
