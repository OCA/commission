# Copyright 2016-2022 Tecnativa - Pedro M. Baeza
{
    "name": "Sales commissions based on Sale Order",
    "author": "Opsway, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "version": "16.0.1.0.0",
    "depends": ["sale_commission", "account_commission"],
    "data": [
        "reports/report_settlement_templates.xml",
        "views/commission_views.xml",
    ],
}
