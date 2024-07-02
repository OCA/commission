#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sales Commissions Agent Restrict",
    "version": "16.0.1.0.0",
    "author": "Ooops404, Ilyas, Odoo Community Association (OCA)",
    "maintainers": ["aleuffre"],
    "category": "Sales",
    "website": "https://github.com/OCA/commission",
    "license": "AGPL-3",
    "depends": [
        "base_rule_visibility_restriction",
        "commission",
        "sale_commission",
        "sales_team",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [
        "demo/res_users_demo.xml",
    ],
    "installable": True,
}
