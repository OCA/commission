# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Commission Product Criteria Discount",
    "summary": "Advanced commissions rules with discount",
    "version": "16.0.1.0.1",
    "author": "Ilyas," "Ooops404," "Odoo Community Association (OCA)",
    "contributors": ["Ilyas"],
    "maintainers": [
        "aleuffre",
        "ilyasProgrammer",
        "renda-dev",
        "PicchiSeba",
    ],
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["sale_commission_product_criteria"],
    "data": [
        "views/views.xml",
        "views/res_config_settings_views.xml",
        "security/base_groups.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
