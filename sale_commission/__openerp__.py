# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015-2016 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# © 2015-2016 Oihane Crucelaegui
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sales commissions',
    'version': '9.0.1.0.0',
    'author': 'Pexego, '
              'Savoir-faire linux, '
              'Avanzosc, '
              'Abstract, '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'product',
        'sale',
    ],
    'contributors': [
        'Davide Corio <davide.corio@domsense.com>',
        'Joao Alfredo Gama Batista <joao.gama@savoirfairelinux.com>',
        'Sandy Carter <sandy.carter@savoirfairelinux.com>',
        'Giorgio Borelli <giorgio.borelli@abstract.it>',
        'Daniel Campos <danielcampos@avanzosc.es>',
        'Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>',
        'Oihane Crucelaegui <oihanecruce@gmail.com>',
        'Iván Todorovich <ivan.todorovich@gmail.com>',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
        'views/sale_commission_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/settlement_view.xml',
        'wizard/wizard_settle.xml',
        'wizard/wizard_invoice.xml',
    ],
    'demo': [
        'demo/sale_agent_demo.xml',
    ],
    'installable': True,
}
