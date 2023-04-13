# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Commission Type Lines",
    "summary": "Advanced commissions rules",
    "version": "14.0.1.0.1",
    "author": "Ilyas," "Ooops404," "Odoo Community Association (OCA)",
    "contributors": ["Ilyas"],
    "maintainers": ["ilyasProgrammer"],
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "license": "LGPL-3",
    "depends": ["sale_commission", "web_domain_field"],
    "data": [
        "views/views.xml",
        "views/res_partner_view.xml",
        "views/res_config_settings_views.xml",
        "views/agent_customer_relation_view.xml",
        "views/agent_commission_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/sale_agent_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
