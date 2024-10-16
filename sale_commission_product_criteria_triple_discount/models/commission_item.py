#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CommissionItem(models.Model):
    _inherit = "commission.item"

    used_discount = fields.Selection(
        selection=[
            ("first", "First"),
            ("computed", "Computed"),
        ],
        default="first",
        string="Used discount",
        help="Discount that has to be in the specified range:\n"
        "- First: the first discount percentage,\n"
        "- Computed: the discount percentage resulting from the triple discount,\n",
    )
