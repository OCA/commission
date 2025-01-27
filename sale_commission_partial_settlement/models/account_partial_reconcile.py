from odoo import fields, models


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    account_invoice_line_agent_partial_ids = fields.One2many(
        "account.invoice.line.agent.partial", "account_partial_reconcile_id"
    )  # Deprecated, left for compatibility with previous versions
