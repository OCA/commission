from odoo import models


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    def action_settle_queued(self):
        self.with_delay().action_settle()
