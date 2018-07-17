# -*- coding: utf-8 -*-
{
    'name': "Sale Commission Brand",

    'summary': """Adds the commissions grouped by brand""",

    'license': 'AGPL-3',

    'author': 'Odoo Community Association (OCA)',

    'category': 'Commission',
    'version': '10.0.2.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_commission',  # OCA commission
                'product_brand'],  # OCA product-attribute

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'application': False,
    'installable': True
}
