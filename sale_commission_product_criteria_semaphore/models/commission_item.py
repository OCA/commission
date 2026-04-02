# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class CommissionItem(models.Model):
    _inherit = "commission.item"
    _order = "applied_on, based_on, categ_id desc, semaphore, id desc"

    semaphore = fields.Selection(
        [
            ("success", "🟢"),
            ("warning", "🟡"),
            ("danger", "🔴"),
        ]
    )
