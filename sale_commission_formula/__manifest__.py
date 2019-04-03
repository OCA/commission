# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sale Commission Formula',
    'version': '10.0.1.0.1',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Sale commissions computed by formulas',
    'author': "Abstract,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/commission/tree/'
               '10.0/sale_commission_formula',
    'depends': [
        'sale_commission'],
    'data': [
        'views/sale_commission_view.xml'],
    'demo': [
        'demo/commission_demo.xml'],
    'installable': True,
}
