# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class CommissionSettlementLine(models.AbstractModel):
    _inherit = "commission.settlement.line"

    semaphore = fields.Selection(
        [
            ("success", "🟢"),
            ("warning", "🟡"),
            ("danger", "🔴"),
        ],
        compute="_compute_semaphore",
        store=True,
    )

    @api.depends("invoice_line_id")
    def _compute_semaphore(self):
        for settlement_line in self:
            settlement_line.semaphore = settlement_line.invoice_line_id.semaphore
