# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
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
    'license': 'GPL-3 or any later version',
    "category": "Generic Modules/Sales & Purchases",
    'depends': [
        'base',
        'account',
        'product',
        'sale'
    ],
    'contributors': [
        "Davide Corio <davide.corio@domsense.com>",
        "Joao Alfredo Gama Batista <joao.gama@savoirfairelinux.com>",
        "Sandy Carter <sandy.carter@savoirfairelinux.com>",
        "Giorgio Borelli <giorgio.borelli@abstract.it>",
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>"],
    "data": [
        "security/ir.model.access.csv",
        "view/sale_agent_view.xml",
        "view/partner_agent_view.xml",
        "wizard/wizard_invoice.xml",
        "wizard/wizard_settle.xml",
        "view/partner_view.xml",
        "view/settled_view.xml",
        "view/invoice_view.xml",
        "view/sale_order_view.xml",
        "view/product_view.xml",
        "report/cc_commission_report.xml"
    ],
    "demo": [
        'demo/sale_agent_demo.xml',
    ],
    "active": True,
    "installable": True
}
