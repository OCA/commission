# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CommissionMakeSettle(models.TransientModel):
    _inherit = "commission.make.settle"

    settlement_type = fields.Selection(
        selection_add=[("invoice", "Invoice")],
        ondelete={"invoice": "cascade"},
    )

    def _get_settlement_line_date(self, line):
        if self.settlement_type == "invoice":
            return line.invoice_date
        return super()._get_settlement_line_date

    def _get_agent_lines(self, agent, date_to_agent):
        if self.settlement_type == "invoice":
            return self.env["account.invoice.line.agent"].search(
                [
                    ("invoice_date", "<", date_to_agent),
                    ("agent_id", "=", agent.id),
                    ("settled", "=", False),
                ],
                order="invoice_date",
            )
        return super()._get_agent_lines
