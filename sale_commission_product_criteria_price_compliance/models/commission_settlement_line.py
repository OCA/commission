# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import api, fields, models


class CommissionSettlementLine(models.AbstractModel):
    _name = "commission.settlement.line"
    _inherit = [
        "commission.settlement.line",
        "product.price.compliance.threshold.tier.mixin",
    ]

    price_compliance_tier = fields.Selection(
        compute="_compute_price_compliance_tier",
        store=True,
    )

    @api.model
    def _get_price_compliance_selection_tiers(self):
        """Dislay texts on selection instead of icon colors."""
        return self._get_price_compliance_selection_tiers_text()

    @api.depends("invoice_line_id")
    def _compute_price_compliance_tier(self):
        for settlement_line in self:
            # Get the first one
            sale_line = settlement_line.invoice_line_id.sale_line_ids[:1]
            settlement_line.price_compliance_tier = sale_line.price_compliance_tier
