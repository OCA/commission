{
    'name': 'Sales commissions',
    'version': '11.0.1.4.3',
    'author': 'Odoo Community Association (OCA)',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'product',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_commission_view.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
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
