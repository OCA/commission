# © 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# Copyright 2020 Andrea Cometa - Apulia Software s.r.l.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sale commissions product',
    'version': '12.0.1.1.1',
    'author': 'Andrea Cometa - Apulia Software s.r.l., '
              'Asr Oss - Alejandro Sánchez, '
              'Odoo Community Association (OCA)',
    "category": "Generic Modules/Sales & Purchases",
    'license': 'AGPL-3',
    'depends': [
        'sale_commission',
    ],
    'contributors': [
        "Andrea Cometa <a.cometa@apuliasoftware.it>",
        "Alejandro Sánchez <alejandro@asr-oss.com>",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
    ],
    "installable": True,
}
