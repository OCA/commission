# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# Copyright 2020 ElvenStudio - Vincenzo Terzulli <v.terzulli@elvenstudio.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    commission_id = fields.Many2one(
        comodel_name='sale.commission',
        string='Commission',
        ondelete='restrict',
    )
