#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, installed_version):
    settlements = env["sale.commission.settlement"].search([
        ("invoice_line_ids", "=", False)
    ])
    for settlement in settlements:
        invoice_ids = settlement.invoice_ids
        settlement.invoice_line_ids = invoice_ids.mapped('invoice_line_ids')
