# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import api, fields, models


class CommissionItem(models.Model):
    _name = "commission.item"
    _inherit = ["commission.item", "product.price.compliance.threshold.tier.mixin"]
    _order = "applied_on, based_on, categ_id desc, price_compliance_tier asc, id desc"

    price_compliance_tier = fields.Selection(
        readonly=False,
    )

    @api.model
    def _get_price_compliance_selection_tiers(self):
        """Dislay texts on selection instead of icon colors."""
        return self._get_price_compliance_selection_tiers_text()
