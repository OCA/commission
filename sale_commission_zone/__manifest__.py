# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Commission Zone',
    'summary': """
        Sale Commission Zone""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/commission',
    'depends': [
        'sale_commission',
        'partner_zone',
    ],
    'data': [
        'views/partner_zone.xml',
        'views/res_partner.xml',
    ],
    'demo': [
    ],
}
