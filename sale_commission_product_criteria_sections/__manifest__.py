# Copyright 2025 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Commission Product Criteria Sections",
    "summary": "Compute product criteria commissions by amount sections",
    "version": "16.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/commission",
    "author": "Madooit, Odoo Community Association (OCA)",
    "maintainers": ["rodmad85"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_commission_product_criteria",
    ],
    "data": [
        "views/commission_views.xml",
    ],
}
