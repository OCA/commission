# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sale Commission Rebate',
    'version': '10.0.1.0.1',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Rebates based on sale volumes',
    'author': "Abstract,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/commission/tree/',
    'data': [
        'views/sale_order_view.xml'],
    'depends': [
        'sale_commission', 'product_supplierinfo_rebate'],
    'installable': True,
}
