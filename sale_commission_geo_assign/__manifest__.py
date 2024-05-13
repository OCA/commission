# Copyright 2018 Lorenzo Battistini <https://github.com/eLBati>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sales commissions - Geo assignation",
    "summary": "Assign agents to partners according to their location",
    "version": "14.0.1.1.1",
    "development_status": "Production/Stable",
    "category": "Sales Management",
    "website": "https://github.com/OCA/commission",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_commission",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "wizard/wizard_geo_assign_partner_view.xml",
    ],
}
