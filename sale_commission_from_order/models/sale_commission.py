from odoo import models, fields


class Commission(models.Model):
    _inherit = "sale.commission"

    invoice_state = fields.Selection(selection_add=[
        ('confirmed_orders', 'Confirmed orders based'),
    ])
