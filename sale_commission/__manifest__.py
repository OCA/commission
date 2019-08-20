# -*- coding: utf-8 -*-

{
    'name': 'Sales commissions',
    'version': '10.0.2.5.0',
    'author': 'Odoo Community Association (OCA),'
              'Tecnativa,'
              'AvanzOSC,'
              'Agile Business Group',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'product',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/sale_commission_view.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/sale_commission_settlement_view.xml',
        'views/sale_commission_settlement_report.xml',
        'views/report_settlement_templates.xml',
        'report/sale_commission_analysis_report_view.xml',
        'wizard/wizard_settle.xml',
        'wizard/wizard_invoice.xml',
    ],
    'demo': [
        'demo/sale_agent_demo.xml',
    ],
    'installable': True,
}
