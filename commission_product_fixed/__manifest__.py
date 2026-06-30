# Copyright 2026 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Commission Product Fixed Amount",
    "version": "19.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/commission",
    "depends": [
        "account_commission_oca",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/commission_views.xml",
    ],
    "installable": True,
}
