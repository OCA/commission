# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
{
    "name": "Commissions",
    "version": "15.0.0.0.1",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["product", "sale_management"],
    "website": "https://github.com/OCA/commission",
    "development_status": "Mature",
    "maintainers": ["pedrobaeza"],
    "data": [
        "security/ir.model.access.csv",
        "views/commission_view.xml",
        "views/commission_mixin_views.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
    ],
    "demo": ["demo/agent_demo.xml"],
    "installable": True,
}
