# Copyright 2020 NextERP Romania SRL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    formula_comm = env["sale.commission"].search([("commission_type", "=", "formula")])
    for com in formula_comm:
        if "account.invoice.line" in com.formula:
            com.formula = com.formula.replace(
                "account.invoice.line", "account.move.line"
            )
