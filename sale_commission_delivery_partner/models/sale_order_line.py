from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_partner_for_commission(self):
        return self.order_id.partner_shipping_id

    @api.depends("order_id", "order_id.partner_shipping_id")
    def _compute_agent_ids(self):
        self.agent_ids = False
        for record in self.filtered(lambda x: x._get_partner_for_commission()):
            if not record.commission_free:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record._get_partner_for_commission()
                )
