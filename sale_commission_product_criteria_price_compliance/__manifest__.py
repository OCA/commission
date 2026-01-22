# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sale Commission Product Criteria - Price Compliance",
    "summary": "Commision rules for Pricing Compliance",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/commission",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_commission_product_criteria",
        "sale_price_compliance",
    ],
    "data": [
        "views/commission_view.xml",
        "views/commission_item_view.xml",
        "views/commission_settlement_view.xml",
        "views/commission_settlement_line_view.xml",
        "report/report_settlement_templates.xml",
    ],
}
