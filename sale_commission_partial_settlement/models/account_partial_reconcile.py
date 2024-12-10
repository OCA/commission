from odoo import api, fields, models


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    # Logically a One2one
    account_invoice_line_agent_partial_ids = fields.One2many(
        "account.invoice.line.agent.partial", "account_partial_reconcile_id"
    )
    partial_commission_settled = fields.Boolean(
        compute="_compute_partial_commission_settled", store=True
    )

    @api.depends(
        "account_invoice_line_agent_partial_ids",
        "account_invoice_line_agent_partial_ids.agent_line.settlement_id.state",
    )
    def _compute_partial_commission_settled(self):
        for rec in self:
            rec.partial_commission_settled = any(
                settlement.state != "cancel"
                for settlement in rec.mapped(
                    "account_invoice_line_agent_partial_ids.agent_line.settlement_id"
                )
            )
