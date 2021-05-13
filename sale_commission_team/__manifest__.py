# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Commission Team',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE, Odoo Community Association (OCA)',
    "category": "Sales",
    'website': 'https://github.com/oca/commission',
    'depends': [
        'sale_commission',
        'sale',
        'sales_team',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/crm_team.xml',
        'views/res_partner.xml',
    ],
    'demo': [
    ],
}
