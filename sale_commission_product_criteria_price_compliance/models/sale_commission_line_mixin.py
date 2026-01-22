# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _commission_items_query_params(self, commission, product):
        res = super()._commission_items_query_params(commission, product)
        # Find the sale.order.line related to its price_compliance_tier
        sale_line = None
        if self.object_id._name == "sale.order.line":
            sale_line = self.object_id
        elif self.object_id._name == "account.move.line":
            sale_line = self.object_id.sale_line_ids[:1]  # Choose the first one
        res["price_compliance_tier"] = (
            sale_line and sale_line.price_compliance_tier or None
        )
        return res

    def _commission_items_where(self):
        res = super()._commission_items_where()
        res = f"""{res} AND (
        item.price_compliance_tier IS NULL
        OR item.price_compliance_tier = %(price_compliance_tier)s
        )"""  # noqa: E202
        return res

    def _commission_items_order(self):
        res = super()._commission_items_order()
        res = f"item.price_compliance_tier asc, {res}"
        return res
