#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from . import models
from odoo import SUPERUSER_ID
from odoo.api import Environment


def set_invoices(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    settlements = env["sale.commission.settlement"].search([
        ("invoice_line_ids", "=", False)
    ])
    for settlement in settlements:
        invoice = settlement.invoice
        settlement.invoice_line_ids = invoice.invoice_line_ids
