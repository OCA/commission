# Copyright 2021 Lorenzo Battistini @ TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sales commissions from sale orders",
    "summary": "Allow to generate commissions from sale orders",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Sales Management",
    "website": "https://github.com/OCA/commission",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_commission",
    ],
    "data": [
        "views/sale_commission_settlement_views.xml",
        "views/settlement_reports.xml",
    ],
}
