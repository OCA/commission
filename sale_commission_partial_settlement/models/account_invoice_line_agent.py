# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    payment_amount_type = fields.Selection(related="commission_id.payment_amount_type")
    partial_settled = fields.Monetary(
        string="Partial Commission Amount Settled",
        compute="_compute_partial_settled",
        store=True,
    )
    is_fully_settled = fields.Boolean(compute="_compute_is_fully_settled", store=True)
    invoice_line_agent_partial_ids = fields.One2many(
        "account.invoice.line.agent.partial",
        "invoice_line_agent_id",
        compute="_compute_invoice_line_agent_partial_ids",
        store=True,
    )
    commission_settlement_line_partial_ids = fields.One2many(
        "sale.commission.settlement.line.partial",
        compute="_compute_commission_settlement_line_partial_ids",
    )

    @api.depends(
        "invoice_line_agent_partial_ids.settled_amount",
    )
    def _compute_partial_settled(self):
        for rec in self:
            rec.partial_settled = sum(
                ailap.settled_amount for ailap in rec.invoice_line_agent_partial_ids
            )

    @api.depends(
        "commission_id.payment_amount_type",
        "amount",
        "settled",
        "partial_settled",
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

    @api.depends(
        "amount",
        "commission_id.payment_amount_type",
        "object_id.move_id.move_type",
        "object_id.move_id.line_ids.amount_residual",
    )
    def _compute_invoice_line_agent_partial_ids(self):
        """
        Create an account.invoice.line.agent.partial for each
        payment term move line
        """
        for rec in self:
            # Prevent compute from running too early
            if not rec.id:
                continue
            ailap_model = rec.invoice_line_agent_partial_ids.browse()
            if rec.commission_id.payment_amount_type != "paid" or rec.amount == 0:
                rec.invoice_line_agent_partial_ids = False
                continue
            pay_term_lines = rec.object_id.move_id.line_ids.filtered(
                lambda line: line.account_internal_type in ("receivable", "payable")
            )
            forecast_lines = rec.invoice_line_agent_partial_ids.mapped("move_line_id")
            for move_line in pay_term_lines:
                if move_line not in forecast_lines:
                    ailap_model.create(
                        {"move_line_id": move_line.id, "invoice_line_agent_id": rec.id}
                    )

    def _compute_commission_settlement_line_partial_ids(self):
        for rec in self:
            rec.commission_settlement_line_partial_ids = (
                rec.invoice_line_agent_partial_ids.settlement_line_partial_ids
            )

    def action_see_partial_commissions(self):
        view = self.env.ref(
            "sale_commission_partial_settlement.account_invoice_line_agent_form_partial_only"
        )
        return {
            "name": _("Partial Commissions"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": self._name,
            "views": [(view.id, "form")],
            "target": "new",
            "res_id": self.id,
        }
