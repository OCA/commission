# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': "website_sale_commission",
    'summary': """
        Add commissions to sale order lines created from the website """,
    'author': 'Odoo Community Association (OCA),'
              'Anybox,',
    'website': "https://github.com/OCA/commission",
    'category': 'Sales Management',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': ['sale', 'website_sale', 'sale_commission'],
    'installable': True,
}