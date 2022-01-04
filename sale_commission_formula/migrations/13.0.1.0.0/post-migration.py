# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    formula_comm = (
        env["sale.commission"]
        .with_context(active_test=False)
        .search([("commission_type", "=", "formula")])
    )
    for com in formula_comm:
        if "account.invoice.line" in com.formula:
            com.formula = com.formula.replace(
                "account.invoice.line", "account.move.line"
            )
