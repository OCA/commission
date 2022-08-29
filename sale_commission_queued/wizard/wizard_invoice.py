from odoo import models


class SaleCommissionMakeInvoice(models.TransientModel):
    _inherit = "sale.commission.make.invoice"

    def button_create_queued(self):
        self.with_delay().create_settlements_and_invoices()
