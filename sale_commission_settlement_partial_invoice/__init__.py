from . import models
from odoo import SUPERUSER_ID
from odoo.api import Environment


def set_invoices(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    settlements = env["sale.commission.settlement"].search([
        ("invoice_ids", "=", False)
    ])
    for settlement in settlements:
        settlement.invoice_ids = [(4, settlement.invoice.id)]
