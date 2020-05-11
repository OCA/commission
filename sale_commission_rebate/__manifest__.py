# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Commission Rebate',
    'version': '10.0.1.0.1',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Rebates based on sale volumes',
    "author": "ForgeFlow S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.github.com/OCA/commission.git",
    'data': [
        'views/sale_order_view.xml'],
    'depends': [
        'sale_commission', 'product_supplierinfo_rebate'],
    'installable': True,
}
