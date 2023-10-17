# -*- coding: utf-8 -*-
from odoo import models, fields


class CommissionMakeSettle(models.TransientModel):
    _inherit = "commission.make.settle"

    settlement_type = fields.Selection(
        selection_add=[("sale_order", "Sales Orders")],
        ondelete={"sale_order": "cascade"},
    )

    def _get_agent_lines(self, agent, date_to_agent):
        """Filter sales order agent lines for this type of settlement."""
        if self.settlement_type == "sale_order":
            domain = self._get_account_settle_domain(agent, date_to_agent)
            return self.env["sale.order.line.agent"].search(domain, order="invoice_date")
        return super()._get_agent_lines(agent, date_to_agent)

    def _get_account_settle_domain(self, agent, date_to_agent):
        return [
            ("invoice_date", "<", date_to_agent),
            ("agent_id", "=", agent.id),
            ("settled", "=", False),
            ("object_id.display_type", "not in", ("line_section", "line_note")),
        ]

    def _prepare_settlement_line_vals(self, settlement, line):
        """Prepare extra settlement values when the source is a sales order agent line."""
        res = super()._prepare_settlement_line_vals(settlement, line)
        if self.settlement_type == "sale_order":
            res.pop('invoice_agent_line_id', None)
            res.update(
                {
                    "sale_agent_line_id": line.id,
                    "date": line.invoice_date,
                    "commission_id": line.commission_id.id,
                    "settled_amount": line.amount,
                }
            )
        return res
