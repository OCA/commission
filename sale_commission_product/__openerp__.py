# -*- coding: utf-8 -*-
# © 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sale commissions product',
    'version': '8.0.1.0.1',
    'author': 'Asr Oss - Alejandro Sánchez, '
              'Odoo Community Association (OCA)',
    "category": "Generic Modules/Sales & Purchases",
    'license': 'AGPL-3',
    'depends': [
        'sale_commission',
        'web_widget_one2many_tags',
    ],
    'contributors': [
        "Alejandro Sánchez <alejandro@asr-oss.com>",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
