from odoo import models


class CommissionMakeInvoice(models.TransientModel):
    _inherit = "commission.make.invoice"

    def button_create_queued(self):
        self.with_delay().button_create()
