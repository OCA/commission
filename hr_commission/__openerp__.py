# -*- coding: utf-8 -*-
# Copyright 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'HR commissions',
    'version': '9.0.1.0.0',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    "category": "Human Resources",
    'license': 'AGPL-3',
    "website": "https://www.tecnativa.com/",
    'depends': [
        'sale_commission',
        'hr'
    ],
    "data": [
        "views/res_partner_view.xml",
    ],
    'installable': True,
    "auto_install": True,
}
