from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id", "order_id.partner_shipping_id")
    def _compute_agent_ids(self):
        self.agent_ids = False
        for record in self.filtered(lambda x: x.order_id.partner_shipping_id):
            if not record.commission_free:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.order_id.partner_shipping_id
                )
