# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#    Copyright (C) 2015 Avanzosc (<http://www.avanzosc.es>)
#    Copyright (C) 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
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
    'version': '2.0',
    'author': 'Pexego, '
              'Savoire-faire linux, '
              'Avanzosc, '
              'Abstract, '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    "category": "Sales Management",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'product',
        'sale'
    ],
    'contributors': [
        "Pexego",
        "Davide Corio <davide.corio@domsense.com>",
        "Joao Alfredo Gama Batista <joao.gama@savoirfairelinux.com>",
        "Sandy Carter <sandy.carter@savoirfairelinux.com>",
        "Giorgio Borelli <giorgio.borelli@abstract.it>",
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "views/sale_commission_view.xml",
        "views/sale_order_view.xml",
        "views/account_invoice_view.xml",
        "views/settlement_view.xml",
        "wizard/wizard_settle.xml",
        "wizard/wizard_invoice.xml",
        # "report/cc_commission_report.xml"
    ],
    "demo": [
        # 'demo/sale_agent_demo.xml',
    ],
    "installable": True
}
