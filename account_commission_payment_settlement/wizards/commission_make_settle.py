# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.osv import expression

from ..models.account_move import PAID_STATES


class CommissionMakeSettle(models.TransientModel):
    _inherit = "commission.make.settle"

    def _get_paid_later_invoice_domain(self, date_to_agent):
        """Invoices with a payment on or after the date limit.

        The payment date is the date of the reconciliation, or the due date of
        the payment journal item when it is later: a payment order confirmed
        today to be collected on a later date keeps that date as due date.
        Refunds keep the reconciliation date, as their due date isn't a payment.
        """
        later_payment_line = [
            ("move_id.move_type", "=", "entry"),
            ("date_maturity", ">=", date_to_agent),
        ]
        return [
            (
                "line_ids",
                "any",
                [
                    "|",
                    (
                        "matched_credit_ids",
                        "any",
                        [
                            "|",
                            ("max_date", ">=", date_to_agent),
                            ("credit_move_id", "any", later_payment_line),
                        ],
                    ),
                    (
                        "matched_debit_ids",
                        "any",
                        [
                            "|",
                            ("max_date", ">=", date_to_agent),
                            ("debit_move_id", "any", later_payment_line),
                        ],
                    ),
                ],
            )
        ]

    def _get_account_settle_domain(self, agent, date_to_agent):
        """Settle payment based commissions only when the invoice is paid before
        the same date limit applied to the invoice date, so settling a past period
        doesn't include the payments received after it. Add the settled lines whose
        payment was undone before that limit, or paid again before it.
        """
        domain = super()._get_account_settle_domain(agent, date_to_agent)
        paid_in_period = [
            ("invoice_id.payment_state", "in", PAID_STATES),
            (
                "invoice_id",
                "not any",
                self._get_paid_later_invoice_domain(date_to_agent),
            ),
        ]
        unsettled_domain = expression.AND(
            [
                domain,
                expression.OR(
                    [[("commission_id.invoice_state", "!=", "paid")], paid_in_period]
                ),
            ]
        )
        # The same conditions for the settled lines with an amount to regularize
        settled_domain = [
            ("settled", "=", True) if leaf == ("settled", "=", False) else leaf
            for leaf in domain
        ]
        regularization_domain = expression.AND(
            [
                settled_domain,
                [("pending_amount", "!=", 0)],
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
