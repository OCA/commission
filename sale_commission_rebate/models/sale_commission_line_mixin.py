# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = 'sale.commission.line.mixin'

    @api.multi
    def _get_commission_amount(
            self, commission, subtotal, commission_free, product, quantity):
        self.ensure_one()
        if commission.commission_type == 'rebate' and \
                not commission_free and commission:
            # purchase price stored in product.suppplierinfo
            # perhaps best to store commission amount in the sale line?
            if self.object_id._name == 'sale.order.line':
                supplierinfo = self.object_id.supplierinfo_id
                if supplierinfo:
                    return (
                        supplierinfo.price - self.object_id.rebate_price) * quantity
            elif self.object_id._name == 'account.invoice.line':
                amount = 0.0
                for sol in self.object_id.sale_line_ids:
                    amount += (sol.supplierinfo_id.price -
                               sol.rebate_price) * quantity
                return amount

        return super(SaleCommissionLineMixin, self)._get_commission_amount(
            commission, subtotal, commission_free, product, quantity)
