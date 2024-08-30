# Copyright 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Commission Product Criteria Domain",
    "version": "14.0.1.0.12",
    "author": "Ilyas," "Ooops404," "Odoo Community Association (OCA)",
    "contributors": ["Ilyas"],
    "maintainers": ["ilyasProgrammer", "aleuffre", "renda-dev", "PicchiSeba"],
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale_commission_product_criteria",
        "web_domain_field",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "data": [
        "views/views.xml",
        "security/ir.model.access.csv",
        "security/sale_commission_security.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
