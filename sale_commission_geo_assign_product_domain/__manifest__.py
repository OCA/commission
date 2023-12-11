# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Commission Geo Assign Product Domain",
    "summary": "Bridge module between "
    "sale_commission_product_criteria_domain and "
    "sale_commission_geo_assign",
    "version": "14.0.1.2.1",
    "author": "PyTech SRL, Ooops404, Odoo Community Association (OCA)",
    "maintainers": ["aleuffre", "renda-dev"],
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale_commission_geo_assign",
        "sale_commission_product_criteria_domain",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": True,
}
