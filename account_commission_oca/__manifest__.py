# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
{
    "name": "Account commissions",
    "version": "15.0.1.0.0",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "account",
        "commission",
    ],
    "website": "https://github.com/OCA/commission",
    "maintainers": ["pedrobaeza"],
    "data": [
        "security/ir.model.access.csv",
        "security/account_commission_security.xml",
        "views/account_move_views.xml",
        "views/account_commission_settlement_view.xml",
        "views/commission_views.xml",
        "views/report_settlement_templates.xml",
        "views/res_partner.xml",
        "report/commission_analysis_view.xml",
    ],
    "installable": True,
}
