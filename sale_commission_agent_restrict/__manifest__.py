{
    "name": "Sales Commissions Agent Restrict",
    "version": "14.0.2.0.1",
    "author": "Ooops404, Ilyas, Odoo Community Association (OCA)",
    "maintainers": ["aleuffre"],
    "category": "Sales",
    "website": "https://github.com/OCA/commission",
    "license": "AGPL-3",
    "depends": [
        "base_rule_visibility_restriction",
        "sale_commission",
        "sales_team",
        "web_domain_field",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
