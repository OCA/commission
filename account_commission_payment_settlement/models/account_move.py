# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

PAID_STATES = ["in_payment", "paid", "reversed"]


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    pending_amount = fields.Monetary(
        compute="_compute_pending_amount",
        store=True,
        help="Payment based commission amount not settled yet: the commission "
        "amount while the invoice is paid, or zero when it is not, minus the "
        "amount already settled.",
    )
    payment_reversal_date = fields.Date(
        readonly=True,
        copy=False,
        help="Last date a payment of the invoice was undone.",
    )

    def _is_payment_received(self):
        self.ensure_one()
        return (
            self.invoice_id.state == "posted"
            and self.invoice_id.payment_state in PAID_STATES
        )

    @api.depends(
        "amount",
        "commission_id.invoice_state",
        "invoice_id.state",
        "invoice_id.payment_state",
        "settlement_line_ids.settled_amount",
        "settlement_line_ids.settlement_id.state",
    )
    def _compute_pending_amount(self):
        for line in self:
            if line.commission_id.invoice_state != "paid":
                line.pending_amount = 0.0
                continue
            due_amount = line.amount if line._is_payment_received() else 0.0
            settled_amount = sum(
                line.settlement_line_ids.filtered(
                    lambda x: x.settlement_id.state != "cancel"
                ).mapped("settled_amount")
            )
            line.pending_amount = line.currency_id.round(due_amount - settled_amount)

    def _skip_settlement(self):
        """Settle the difference of an already settled line, paid or not: the
        wizard search already applies the date limits.
        """
        self.ensure_one()
        if self.settled and self.pending_amount:
            return False
        return super()._skip_settlement()
