from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SettlementLinePartial(models.Model):
    _name = "sale.commission.settlement.line.partial"
    _description = "Partial settlements. "
    "Tracks the effective settled amounts relative to the expected."

    settlement_line_ids = fields.Many2many(
        comodel_name="sale.commission.settlement.line",
        relation="settlement_line_line_partial_rel",
    )
    invoice_agent_partial_id = fields.Many2one(
        comodel_name="account.invoice.line.agent.partial",
        required=True,
        ondelete="cascade",
    )
    partial_reconcile_id = fields.Many2one(
        comodel_name="account.partial.reconcile",
        required=True,
        ondelete="cascade",
    )
    amount = fields.Monetary(
        compute="_compute_amount",
        store=True,
    )
    move_id = fields.Many2one(related="invoice_agent_partial_id.move_id")
    company_id = fields.Many2one(related="move_id.company_id")
    invoice_line_id = fields.Many2one(
        related="invoice_agent_partial_id.invoice_line_id"
    )
    invoice_date = fields.Date(
        related="invoice_agent_partial_id.invoice_date", store=True
    )
    invoice_line_agent_id = fields.Many2one(
        related="invoice_agent_partial_id.invoice_line_agent_id"
    )
    agent_id = fields.Many2one(
        related="invoice_agent_partial_id.agent_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="invoice_agent_partial_id.currency_id")
    reconcile_amount = fields.Monetary(
        related="partial_reconcile_id.amount", string="Payment amount"
    )
    date_maturity = fields.Date(
        related="partial_reconcile_id.max_date", store=True, index=True
    )
    reconcile_debit_move_id = fields.Many2one(
        "account.move.line",
        related="partial_reconcile_id.debit_move_id",
        string="Debit move line",
    )
    reconcile_credit_move_id = fields.Many2one(
        "account.move.line",
        related="partial_reconcile_id.credit_move_id",
        string="Credit move line",
    )
    # Mostly to ease user navigation
    settlement_id = fields.Many2one(
        "sale.commission.settlement",
        compute="_compute_settlement_id",
        store=True,
    )
    is_settled = fields.Boolean(
        compute="_compute_settlement_id", store=True, index=True
    )

    def name_get(self):
        return [
            (
                rec.id,
                "%(invoice_line)s - %(amount)s"
                % {
                    "invoice_line": rec.invoice_line_id.display_name,
                    "amount": rec.amount,
                },
            )
            for rec in self
        ]

    @api.depends(
        "partial_reconcile_id.amount",
        "invoice_agent_partial_id.invoice_line_agent_id.amount",
        "invoice_agent_partial_id.move_id.amount_total",
    )
    def _compute_amount(self):
        for rec in self:
            # partial_reconcile_id.amount is unsigned
            # invoice_agent_partial_id.move_id.amount_total is unsigned
            # -> Sign depends only on
            # invoice_agent_partial_id.invoice_line_agent_id.amount
            rec.amount = (
                rec.partial_reconcile_id.amount
                * rec.invoice_agent_partial_id.invoice_line_agent_id.amount
                / rec.invoice_agent_partial_id.move_id.amount_total
            )

    @api.depends("settlement_line_ids.settlement_id.state")
    def _compute_settlement_id(self):
        for rec in self:
            settlements = rec.settlement_line_ids.mapped("settlement_id").filtered(
                lambda x: x.state != "cancel"
            )
            rec.settlement_id = settlements[:1]
            rec.is_settled = bool(settlements)

    def unlink(self):
        for rec in self:
            if rec.is_settled:
                raise UserError(
                    _(
                        "Cannot delete Partial Settlement Line "
                        "for agent %(agent_name)s, amount %(amount)s, "
                        "date maturity %(date_maturity)s because it is "
                        "already part of a settlement",
                        agent_name=rec.agent_id.display_name,
                        amount=rec.amount,
                        date_maturity=rec.date_maturity,
                    )
                )
        super().unlink()
