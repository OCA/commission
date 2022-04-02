# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
{
    "name": "Sales commissions",
    "version": "15.0.0.0.1",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "account",
        "product",
        "sale_management",
        "commission",
    ],
    "website": "https://github.com/OCA/commission",
    "development_status": "Mature",
    "maintainers": ["pedrobaeza"],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_commission_security.xml",
        "views/sale_order_view.xml",
        "views/account_move_views.xml",
        "views/sale_commission_settlement_view.xml",
        "views/sale_commission_settlement_report.xml",
        "views/report_settlement_templates.xml",
        "wizard/wizard_settle.xml",
        "wizard/wizard_invoice.xml",
    ],
    "installable": True,
}
