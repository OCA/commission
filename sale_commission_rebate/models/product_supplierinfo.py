# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.multi
    def name_get(self):
        if not self._context.get('show_rebate_dates', False):
            return super(ProductSupplierinfo, self).name_get()
        result = []
        for sinfo in self:
            name = sinfo.name.name
            if sinfo.date_start:
                name = ' / '.join([name, sinfo.date_start])
            if sinfo.date_end:
                name = ' / '.join([name, sinfo.date_end])
            result.append((sinfo.id, name))
        return result
