# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# Copyright 2020 ElvenStudio - Vincenzo Terzulli <v.terzulli@elvenstudio.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Sales commissions by pricelist',
    'version': '8.0.1.0.0',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'category': 'Sale',
    'website': 'https://github.com/OCA/commission',
    'license': 'AGPL-3',
    'depends': [
        'sale_commission',
    ],
    'data': [
        'views/product_pricelist_view.xml',
    ],
    'installable': True,
}
