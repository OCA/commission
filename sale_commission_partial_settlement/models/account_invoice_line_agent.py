# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    partial_settled = fields.Monetary(string="Partial Commission Amount Settled")

    def _compute_settled(self):
        filtered_lines = self.filtered(
            lambda x: x.commission_id.payment_amount_type != "paid"
        )
        for line in self - filtered_lines:
            if not line.settlement_line_ids:
                line.settled = False

        return super(AccountInvoiceLineAgent, filtered_lines)._compute_settled()

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
        lines_to_update = {}
        for line in self:
            line_total_amount = line.amount
            reconciled_partials, _ = line.invoice_id._get_reconciled_invoices_partials()
            for (
                partial,
                amount,
                counterpart_line,
            ) in reconciled_partials:
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
                        self._partial_agent_line_values(line, line_total_amount)
                    )
                    lines_to_update[line.id] = {
                        "partial_settled": line_total_amount,
                        "settled": True,
                    }
                    partial_payment_remaining[partial.id] = {
                        "remaining_amount": amount - line.object_id.price_total
                    }
                    break

                paid_in_proportion = payment_amount / line.invoice_id.amount_total
                partial_commission = (
                    line.invoice_id.commission_total * paid_in_proportion
                )
                partial_lines_to_settle.append(
                    self._partial_agent_line_values(line, partial_commission)
                )
                if line.id in lines_to_update:
                    lines_to_update[line.id]["partial_settled"] += partial_commission
                else:
                    lines_to_update[line.id] = {"partial_settled": partial_commission}

                if lines_to_update[line.id]["partial_settled"] >= line_total_amount:
                    lines_to_update[line.id].update({"settled": True})
                    break
                partial.partial_commission_settled = True
        partial_agent_lines = self.env["account.invoice.line.agent.partial"].create(
            partial_lines_to_settle
        )
        return partial_agent_lines, lines_to_update

    def _partial_agent_line_values(self, line, amount):
        return {
            "invoice_line_agent_id": line.id,
            "currency_id": line.currency_id.id,
            "amount": amount,
        }
