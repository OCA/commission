{
    "name": "Commissions",
    "version": "15.0.1.0.0",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["product", "sale_management"],
    "website": "https://github.com/OCA/commission",
    "maintainers": ["pedrobaeza"],
    "data": [
        "security/ir.model.access.csv",
        "views/commission_view.xml",
        "views/commission_mixin_view.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
    ],
    "demo": ["demo/commission_and_agent_demo.xml"],
    "installable": True,
}
