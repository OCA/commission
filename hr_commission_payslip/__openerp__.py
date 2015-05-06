# -*- coding: utf-8 -*-
##############################################################################
#
#    KMEE, KM Enterprising Engineering
#    Copyright(C) 2015 - Daniel Sadamo <daniel.sadamo@kmee.com.br>
#
#    This program is free software: you can redistribute it and    /or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

{
    'name': u'Commission in Payslip',
    'version': '1.0',
    'category': 'Other',
    'description': u"""Module to integrate sale_commission module and
    hr_payroll module. Creating a salary rule for commission and auto
    complete the commission input in the payslip""",
    'author': 'KMEE/Odoo Community Association(OCA)',
    'website': 'http://www.kmee.com.br',
    'depends': [
        'sale_commission',
        'hr_payroll',
    ],
    'init_xml': [
        'data/commission_salary_rule_data.xml'
    ],
    'data': [
        'view/hr_payslip.xml'
    ],
    'installable': True,
}
