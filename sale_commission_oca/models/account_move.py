# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    def _get_refunded_agent_lines(self, commission):
        """Extend the hook: without a reversed invoice, take the latest posted
        invoice of the sale order lines, then the sale order lines themselves."""
        agent_lines = super()._get_refunded_agent_lines(commission)
        if agent_lines:
            return agent_lines
        refund_line = self.object_id
        if not refund_line.move_id.reversed_entry_id:
            invoice_lines = refund_line.sale_line_ids.invoice_lines.filtered(
                lambda x: x.move_id.move_type == "out_invoice"
                and x.parent_state == "posted"
            ).sorted(lambda x: (x.date, x.id))[-1:]
            agent_lines = self._get_agent_lines_of(invoice_lines, commission)
        return agent_lines or self._get_agent_lines_of(
            refund_line.sale_line_ids, commission
        )
