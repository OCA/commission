# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Commission Product Criteria",
    "summary": "Advanced commissions rules",
    "version": "15.0.1.0.0",
    "author": "Ilyas, Ooops404, Odoo Community Association (OCA)",
    "maintainers": ["ilyasProgrammer", "aleuffre", "renda-dev", "PicchiSeba"],
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["sale_commission", "web_domain_field"],
    "data": [
        "reports/report_settlement_template.xml",
        "views/views.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/sale_agent_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
