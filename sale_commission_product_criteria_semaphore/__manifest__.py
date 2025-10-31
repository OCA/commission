# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Commission Product Criteria Semaphore",
    "summary": "Add semaphore for advanced commissions rules",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["CarlosRoca13"],
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["sale_commission_product_criteria", "sale_semaphore"],
    "data": [
        "reports/report_settlement_templates.xml",
        "views/commission_item_views.xml",
        "views/commission_settlement_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
