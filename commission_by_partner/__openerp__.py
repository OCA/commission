# -*- coding: utf-8 -*-
# © 2015 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# © 2015 Javier Colmenero Fernández (<javier@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Sale commissions by partner',
    'version': '8.0.2.4.1',
    'author': 'Comunitea',
    "category": "Sales Management",
    'license': 'AGPL-3',
    'depends': [
        'sale_commission',
    ],
    'contributors': [
        "Comunitea",
        "Javier Colmenero Fernández <javier@comunitea.com>",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/partner_agent_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
    ],
    "demo": [
    ],
    'test': [
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
