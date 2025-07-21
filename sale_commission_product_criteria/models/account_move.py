# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    applied_commission_item_id = fields.Many2one("commission.item")

    @api.depends(
        "object_id.price_subtotal",
        "object_id.product_id.commission_free",
        "commission_id",
    )
    def _compute_amount(self):
        res = super(AccountInvoiceLineAgent, self)._compute_amount()
        for line in self:
            if line.commission_id and line.commission_id.commission_type == "product":
                inv_line = line.object_id
                line.amount = line._get_single_commission_amount(
                    line.commission_id,
                    inv_line.price_subtotal,
                    inv_line.product_id,
                    inv_line.quantity,
                )
        return res
