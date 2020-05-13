# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = 'sale.commission.line.mixin'

    @api.multi
    def _get_valid_rebate(self, commission, subtotal, commission_free, product, quantity):
        rebate = self.env['product.supplierinfo'].search(
            [('name', '=', self.agent.id),
             ('product_id', '=', product.id),
             ('product_qty', '<=', quantity),
             ('date_start', '<=', self.agent.object_id.date),
             ('date_end', '>=', self.agent.object_id.date)], limit=1)
        if rebate:
            return rebate
        else:
            raise exceptions.ValidationError(_('No rebate found'))
    @api.multi
    def _get_commission_amount(
            self, commission, subtotal, commission_free, product, quantity):
        self.ensure_one()
        if commission.commission_type == 'rebate' and \
                not commission_free and commission:
            # rebates stored in product.suppplierinfo
            rebate = self._get_valid_rebate()
            return rebate.list_price - rebate.rebate_price
        return super(SaleCommissionLineMixin, self)._get_commission_amount(
            commission, subtotal, commission_free, product, quantity)
