# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Commissions in contract invoices',
    'version': '12.0.1.0.0',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.tecnativa.com/',
    'category': 'Generic Modules/Sales & Purchases',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'depends': [
        'contract',
        'sale_commission',
    ],
    'installable': True,
    'auto_install': True,
}
