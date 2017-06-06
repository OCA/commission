# -*- coding: utf-8 -*-
# © 2015-2016 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# © 2016 Oihane Crucelaegui
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'HR commissions',
    'version': '9.0.1.0.0',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'category': 'Human Resources',
    'depends': [
        'sale_commission',
        'hr',
    ],
    'license': 'AGPL-3',
    'contributors': [
        'Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>',
        'Oihane Crucelaegui <oihanecruce@gmail.com>',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
