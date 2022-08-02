#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': "Sales commissions based on product",
    'summary': "Create commissions based on product",
    'author': "TAKOBI, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/commission",
    'license': "AGPL-3",
    'category': 'Sales',
    'version': '12.0.1.0.0',
    'depends': [
        'sale_commission',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_commission_views.xml',
    ],
}
