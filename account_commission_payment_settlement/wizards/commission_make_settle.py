# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.osv import expression

from ..models.account_move import PAID_STATES


class CommissionMakeSettle(models.TransientModel):
    _inherit = "commission.make.settle"

    def _get_paid_later_invoices_query(self, date_to_agent):
        """Invoices with a payment on or after the date limit.

        The payment date is the date of the reconciliation, or the due date of
        the payment journal item when it is later: a payment order confirmed
        today to be collected on a later date keeps that date as due date.
        Refunds keep the reconciliation date, as their due date isn't a payment.
        """
        later_payment_lines = self.env["account.move.line"]._search(
            [
                ("move_id.move_type", "=", "entry"),
                ("date_maturity", ">=", date_to_agent),
            ]
        )
        return self.env["account.move"]._search(
            [
                "|",
                "|",
                "|",
                ("line_ids.matched_credit_ids.max_date", ">=", date_to_agent),
                ("line_ids.matched_debit_ids.max_date", ">=", date_to_agent),
                (
                    "line_ids.matched_credit_ids.credit_move_id",
                    "in",
                    later_payment_lines,
                ),
                (
                    "line_ids.matched_debit_ids.debit_move_id",
                    "in",
                    later_payment_lines,
                ),
            ]
        )

    def _get_account_settle_domain(self, agent, date_to_agent):
        """Settle payment based commissions only when the invoice is paid before
        the same date limit applied to the invoice date, so settling a past period
        doesn't include the payments received after it. Add the settled lines whose
        payment was undone before that limit, or paid again before it.
        """
        domain = super()._get_account_settle_domain(agent, date_to_agent)
        paid_later_invoices = self._get_paid_later_invoices_query(date_to_agent)
        paid_in_period = [
            ("invoice_id.payment_state", "in", PAID_STATES),
            ("invoice_id", "not in", paid_later_invoices),
        ]
        unsettled_domain = expression.AND(
            [
                domain,
                expression.OR(
                    [[("commission_id.invoice_state", "!=", "paid")], paid_in_period]
                ),
            ]
        )
        regularization_domain = expression.AND(
            [
                [
                    ("invoice_date", "<", date_to_agent),
                    ("agent_id", "=", agent.id),
                    ("settled", "=", True),
                    ("pending_amount", "!=", 0),
                ],
                expression.OR(
                    [
                        paid_in_period,
                        [
                            ("invoice_id.payment_state", "not in", PAID_STATES),
                            "|",
                            ("payment_reversal_date", "=", False),
                            ("payment_reversal_date", "<", date_to_agent),
                        ],
                    ]
                ),
            ]
        )
        return expression.OR([unsettled_domain, regularization_domain])

    def _prepare_settlement_line_vals(self, settlement, line):
        res = super()._prepare_settlement_line_vals(settlement, line)
        if self.settlement_type == "sale_invoice" and line.settled:
            res["settled_amount"] = line.pending_amount
            if not line._is_payment_received() and line.payment_reversal_date:
                res["date"] = line.payment_reversal_date
        return res
