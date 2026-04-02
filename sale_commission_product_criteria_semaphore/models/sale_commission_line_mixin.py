# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
from odoo.osv import expression


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _get_commission_items_domain(self, commission, product):
        domain = super()._get_commission_items_domain(commission, product)
        domain = expression.AND(
            [
                domain,
                [
                    "|",
                    ("semaphore", "=", "False"),
                    ("semaphore", "=", self.object_id.semaphore),
                ],
            ]
        )
        return domain
