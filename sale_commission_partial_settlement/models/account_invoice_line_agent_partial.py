# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceLineAgentPartial(models.Model):
    _name = "account.invoice.line.agent.partial"
    _description = "Partial agent commissions. "
    "Tracks the expected commissions."

    move_line_id = fields.Many2one(
        "account.move.line",
        required=True,
        ondelete="cascade",
    )
    invoice_line_agent_id = fields.Many2one(
        "account.invoice.line.agent", required=True, ondelete="cascade"
    )
    settlement_line_partial_ids = fields.One2many(
        "sale.commission.settlement.line.partial",
        "invoice_agent_partial_id",
        compute="_compute_settlement_line_partial_ids",
        store=True,
    )
    account_partial_reconcile_id = fields.Many2one(
        "account.partial.reconcile"
    )  # Deprecated, left for compatibility with previous versions
    amount = fields.Monetary(
        compute="_compute_amount",
        store=True,
        string="Commission Amount",
    )
    currency_id = fields.Many2one(
        related="invoice_line_agent_id.currency_id",
    )
    settled_amount = fields.Monetary(
        compute="_compute_settled_amount",
        store=True,
    )
    is_settled = fields.Boolean(
        compute="_compute_settled_amount", store=True, string="Fully settled"
    )

    move_id = fields.Many2one(related="move_line_id.move_id", string="Invoice")
    date_maturity = fields.Date(
        related="move_line_id.date_maturity",
        store=True,
    )
    invoice_line_id = fields.Many2one(
        related="invoice_line_agent_id.object_id", string="Invoice Line"
    )
    agent_id = fields.Many2one(
        related="invoice_line_agent_id.agent_id",
        store=True,
    )
    invoice_date = fields.Date(
        related="invoice_line_agent_id.invoice_date",
        store=True,
    )
    company_id = fields.Many2one("res.company", related="move_id.company_id")

    @api.depends(
        "settlement_line_partial_ids.amount",
        "settlement_line_partial_ids.is_settled",
    )
    def _compute_settled_amount(self):
        for rec in self:
            rec.settled_amount = sum(
                x.currency_id._convert(
                    x.amount,
                    rec.currency_id,
                    rec.company_id,
                    rec.date_maturity or rec.move_id.invoice_date,
                )
                for x in rec.settlement_line_partial_ids
                if x.is_settled
            )
            rec.is_settled = rec.currency_id.is_zero(rec.settled_amount - rec.amount)

    @api.depends(
        "move_line_id.balance",
        "move_line_id.move_id.amount_total",
        "invoice_line_agent_id.amount",
    )
    def _compute_amount(self):
        for rec in self:
            # move_line_id.balance
            # invoice_line_agent_id.amount
            # move_line_id.move_id.amount_total_signed
            # all 3 terms are signed
            rec.amount = (
                rec.move_line_id.balance
                * rec.invoice_line_agent_id.amount
                / rec.move_line_id.move_id.amount_total_signed
            )

    @api.depends(
        "invoice_line_agent_id.amount",
        "move_line_id.matched_debit_ids",
        "move_line_id.matched_credit_ids",
    )
    def _compute_settlement_line_partial_ids(self):
        """
        Cf. method _get_reconciled_invoices_partials
        in odoo.addons.account.models.account_move.AccountMove.
        """
        for rec in self:
            if not rec.invoice_line_agent_id.amount:
                rec.settlement_line_partial_ids = False
                continue
            pay_term_line = rec.move_line_id
            matched_partials = (
                pay_term_line.matched_debit_ids + pay_term_line.matched_credit_ids
            )
            if not matched_partials:
                continue
            existing_partial_settlements = rec.settlement_line_partial_ids
            existing_partials = existing_partial_settlements.mapped(
                "partial_reconcile_id"
            )

            for partial in matched_partials:
                if partial not in existing_partials:
                    existing_partial_settlements.create(
                        {
                            "partial_reconcile_id": partial.id,
                            "invoice_agent_partial_id": rec.id,
                        }
                    )
