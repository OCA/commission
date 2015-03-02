# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#   Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Sales commissions',
    'version': '1.1',
    'author': "Pexego,Odoo Community Association (OCA)",
    "category": "Generic Modules/Sales & Purchases",
    'depends': [
        'base',
        'account',
        'product',
        'sale',
        'hr',
        'stock'
    ],
    'description': """
Sales commissions
=================

This modules allow you to define sales agents and assign customers to them.
You can then generate the supplier invoices to pay their commissions.

Video : http://www.youtube.com/watch?v=NDqRnF1qKS0

Contributors
============
Davide Corio <davide.corio@domsense.com>
Joao Alfredo Gama Batista <joao.gama@savoirfairelinux.com>
Sandy Carter <sandy.carter@savoirfairelinux.com>
    """,
    'data': [
        'security/ir.model.access.csv',
        'sale_agent_view.xml',
        'partner_agent_view.xml',
        'wizard/wizard_invoice.xml',
        'partner_view.xml',
        'settled_view.xml',
        'invoice_view.xml',
        'sale_order_view.xml',
        'product_view.xml',
        'stock_picking_view.xml',
        'cc_commission_report.xml',
    ],
    'demo': [
    ],
    'active': False,
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
