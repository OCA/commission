from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id.partner_shipping_id")
    def _compute_agent_ids(self):
        super()._compute_agent_ids()
