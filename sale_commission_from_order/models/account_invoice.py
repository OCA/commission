from odoo import models, api


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    @api.depends(
        "agent_line", "agent_line.settlement.state", "invoice", "invoice.state",
        "object_id.sale_line_ids.agents.agent"
    )
    def _compute_settled(self):
        for line in self:
            super(AccountInvoiceLineAgent, line)._compute_settled()
            if not line.settled:
                # If not settled through invoice, check orders
                agent_lines = self.env["sale.order.line.agent"]
                sale_lines = line.object_id.sale_line_ids
                for sale_line in sale_lines:
                    for sale_agent_line in sale_line.agents:
                        if sale_agent_line.agent.id == line.agent.id:
                            agent_lines |= sale_agent_line
                settlement_lines = agent_lines.mapped("agent_line")
                line.settled = (any(
                    x.settlement.state != "cancel" for x in settlement_lines
                ))

    def _check_settle_integrity(self):
        for record in self:
            if record.agent_line:
                super(AccountInvoiceLineAgent, record)._check_settle_integrity()
