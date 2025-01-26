# Copyright 2025 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Commission Settlement Report Xlsx",
    "summary": """
        Settings to customize the settlement report in xlsx""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/commission",
    "depends": [
        "sale_commission",
        "report_xlsx",
    ],
    "data": ["report/report_settlement_xlsx.xml"],
    "demo": [],
}
