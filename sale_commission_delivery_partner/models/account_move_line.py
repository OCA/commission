from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id", "move_id.partner_shipping_id")
    def _compute_agent_ids(self):
        self.agent_ids = False
        for record in self.filtered(lambda x: x.move_id.partner_shipping_id):
            if not record.commission_free:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.move_id.partner_shipping_id
                )
