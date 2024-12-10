# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    partial_settled = fields.Monetary(
        string="Partial Commission Amount Settled",
        compute="_compute_partial_settled",
        store=True,
    )
    is_fully_settled = fields.Boolean(compute="_compute_is_fully_settled", store=True)
    invoice_line_agent_partial_ids = fields.One2many(
        "account.invoice.line.agent.partial", "invoice_line_agent_id"
    )

    @api.depends(
        "invoice_line_agent_partial_ids.amount",
        "invoice_line_agent_partial_ids.agent_line.settlement_id.state",
    )
    def _compute_partial_settled(self):
        for rec in self:
            rec.partial_settled = sum(
                ailap.amount
                for ailap in rec.invoice_line_agent_partial_ids
                if any(
                    settlement.state != "cancel"
                    for settlement in ailap.mapped("agent_line.settlement_id")
                )
            )

    @api.depends(
        "commission_id.payment_amount_type", "amount", "settled", "partial_settled"
    )
    def _compute_is_fully_settled(self):
        for rec in self:
            if rec.commission_id.payment_amount_type != "paid":
                rec.is_fully_settled = rec.settled
            else:
                rec.is_fully_settled = rec.settled and (
                    float_compare(
                        rec.partial_settled,
                        rec.amount,
                        precision_rounding=rec.currency_id.rounding,
                    )
                    == 0
                )

    def _partial_commissions(self, date_payment_to):
        """
        This method iterates through agent invoice lines and calculates
        partial commissions based on the payment amount.
        If the partial payment amount is greater than the invoice line
        amount, it fully settles the corresponding agent line.
        Otherwise, it calculates the partial commission proportionally to
        the amount paid, invoice amount and total commissions.
        """
        partial_lines_to_settle = []
        partial_payment_remaining = {}
        for line in self:
            line_total_amount = line.amount
            for (
                partial,
                amount,
                counterpart_line,
            ) in line.invoice_id._get_reconciled_invoices_partials():
                if partial.partial_commission_settled:
                    continue
                elif date_payment_to and date_payment_to < counterpart_line.date:
                    break
                if partial.id in partial_payment_remaining:
                    payment_amount = partial_payment_remaining[partial.id][
                        "remaining_amount"
                    ]
                else:
                    payment_amount = amount
                    partial_payment_remaining[partial.id] = {"remaining_amount": amount}
                if line.object_id.price_total <= payment_amount:
                    partial_lines_to_settle.append(
                        {
                            "invoice_line_agent_id": line.id,
                            "currency_id": line.currency_id.id,
                            "amount": line_total_amount,
                            "account_partial_reconcile_id": partial.id,
                        }
                    )
                    partial_payment_remaining[partial.id] = {
                        "remaining_amount": amount - line.object_id.price_total
                    }
                    break

                paid_in_proportion = payment_amount / line.invoice_id.amount_total
                partial_commission = (
                    line.invoice_id.commission_total * paid_in_proportion
                )
                partial_lines_to_settle.append(
                    {
                        "invoice_line_agent_id": line.id,
                        "currency_id": line.currency_id.id,
                        "amount": partial_commission,
                        "account_partial_reconcile_id": partial.id,
                    }
                )
        partial_agent_lines = self.env["account.invoice.line.agent.partial"].create(
            partial_lines_to_settle
        )
        return partial_agent_lines
