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
        .sudo()
        .search([("active", "=", False), ("name", "in", PREDEFINED_RULES)])
    )
    if rules:
        rules.sudo().write({"active": True})
