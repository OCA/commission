from odoo import api, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends("object_id.order_id.pricelist_id")
    def _compute_commission_id(self):
        res = super()._compute_commission_id()
        for record in self:
            commission = record.object_id._get_commission_from_pricelist()
            record.commission_id = commission or record.agent_id.commission_id
        return res
