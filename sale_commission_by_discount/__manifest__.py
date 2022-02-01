{
    'name': 'Sale Commission by Discount',
    'summary': "Advanced commissions rules",
    'version': '14.0.1.0.1',
    "author": "Ooops",
    "contributors": ['Ilyas'],
    "maintainers": ['ilyasProgrammer'],
    "category": "Sales Management",
    "license": "LGPL-3",
    'depends': [
        'sale_commission'  # OCA
    ],
    'data': [
        "views/views.xml",
        "security/ir.model.access.csv",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
