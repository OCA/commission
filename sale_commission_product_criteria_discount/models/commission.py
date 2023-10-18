# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CommissionItem(models.Model):
    _inherit = "commission.item"
    _order = "applied_on, based_on, categ_id desc, id desc, discount_from, discount_to"

    based_on = fields.Selection(
        selection_add=[("discount", "Discount")],
        ondelete={"discount": "set default"},
    )
    discount_from = fields.Float()
    discount_to = fields.Float()

    @api.onchange("based_on")
    def onchange_based_on(self):
        if self.based_on != "discount":
            self.update({"discount_from": 0, "discount_to": 0})

    @api.constrains("discount_from", "discount_to")
    def _check_discounts(self):
        if any(item.discount_from > item.discount_to for item in self):
            raise ValidationError(
                _("Discount From should be lower than the Discount To.")
            )
        return True
