# Copyright 2016 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Davide Corio - Abstract
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Commission Formula",
    "version": "15.0.1.0.0",
    "category": "Commission",
    "license": "AGPL-3",
    "summary": "Commissions computed by formulas",
    "author": "Abstract,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/commission",
    "depends": ["commission"],
    "data": ["views/commission_view.xml"],
    "demo": ["demo/commission_demo.xml"],
    "assets": {
        "web.assets_backend": [
            "commission_formula/static/src/css/commission_formula.css",
        ],
    },
    "installable": True,
}
