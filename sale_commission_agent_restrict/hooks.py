#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api

# -- List of predefined rules that must be managed
PREDEFINED_RULES = [
    "res.partner.rule.private.employee",
    "res.partner.rule.private.group",
]


# -- Restore access rules after module uninstalled
def restore_access_rules(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rules = (
        env["ir.rule"]
        .search([("active", "=", False), ("name", "in", PREDEFINED_RULES)])
    )
    if rules:
        rules.write({"active": True})
