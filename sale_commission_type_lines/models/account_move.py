# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    @api.depends(
        "object_id.price_subtotal",
        "object_id.product_id.commission_free",
        "commission_id",
        "commission_ids",
    )
    def _compute_amount(self):
        for line in self:
            inv_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                line.commission_ids,
                inv_line.price_subtotal,
                inv_line.product_id,
                inv_line.quantity,
            )
            # Refunds commissions are negative
            if line.invoice_id.move_type and "refund" in line.invoice_id.move_type:
                line.amount = -line.amount

    def _skip_settlement(self):
        """This function should return False if the commission can be paid.

        :return: bool
        """
        self.ensure_one()
        if self.commission_ids:
            return (
                all([r.invoice_state == "paid" for r in self.commission_ids])
                and self.invoice_id.payment_state not in ["in_payment", "paid"]
            ) or self.invoice_id.state != "posted"
        else:
            return (
                self.commission_id.invoice_state == "paid"
                and self.invoice_id.payment_state not in ["in_payment", "paid"]
            ) or self.invoice_id.state != "posted"
