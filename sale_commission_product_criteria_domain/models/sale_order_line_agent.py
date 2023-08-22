# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends(
        "object_id.price_subtotal", "object_id.product_id", "object_id.product_uom_qty"
    )
    def _compute_amount(self):
        for line in self:
            if (
                line.commission_id
                and line.commission_id.commission_type == "product_restricted"
            ):
                order_line = line.object_id
                line.amount = line._get_single_commission_amount(
                    line.commission_id,
                    order_line.price_subtotal,
                    order_line.product_id,
                    order_line.product_uom_qty,
                )
            else:
                super(SaleOrderLineAgent, line)._compute_amount()
