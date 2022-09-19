# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
{
    "name": "Commissions",
    "version": "15.0.1.0.0",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "category": "Invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "website": "https://github.com/OCA/commission",
    "maintainers": ["pedrobaeza"],
    "data": [
        "security/ir.model.access.csv",
        "data/menuitem_data.xml",
        "views/account_move_view.xml",
        "security/commission_security.xml",
        "views/commission_views.xml",
        "views/commission_settlement_views.xml",
        "views/commission_mixin_views.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        "views/commission_settlement_report.xml",
        "views/report_settlement_templates.xml",
        "wizards/wizard_invoice.xml",
        "wizards/wizard_settle.xml",
    ],
    "demo": ["demo/commission_and_agent_demo.xml"],
    "installable": True,
}
