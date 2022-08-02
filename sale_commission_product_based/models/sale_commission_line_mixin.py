#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleCommissionLineMixin (models.AbstractModel):
    _inherit = 'sale.commission.line.mixin'

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        self.ensure_one()
        if not product.commission_free \
           and commission.commission_type == 'product_fallback':
            return commission.calculate_product_fallback(subtotal, product)
        return super()._get_commission_amount(
            commission, subtotal, product, quantity,
        )
