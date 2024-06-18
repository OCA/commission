from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.partner_shipping_id")
    def _compute_agent_ids(self):
        super()._compute_agent_ids()
