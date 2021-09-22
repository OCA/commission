from odoo import models, fields, api


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    sale_order_id = fields.Many2one(
        string="Order",
        comodel_name="sale.order",
        related="object_id.order_id",
        store=True,
    )
    agent_line = fields.Many2many(
        comodel_name="sale.commission.settlement.line",
        relation="settlement_agent_sale_line_rel",
        column1="agent_sale_line_id",
        column2="settlement_id",
        copy=False,
    )
    settled = fields.Boolean(
        compute="_compute_settled",
        store=True,
    )
    order_date = fields.Datetime(
        string="Order date",
        related="sale_order_id.date_order",
        store=True,
        readonly=True,
    )
    order_state = fields.Selection(
        [
            ("draft", "Quotation"),
            ("sent", "Quotation Sent"),
            ("sale", "Sales Order"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        "Order status", related="sale_order_id.state",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        compute="_compute_company",
        store=True,
    )

    @api.depends("object_id.company_id")
    def _compute_company(self):
        for line in self:
            line.company_id = line.object_id.company_id

    @api.depends(
        "agent_line.settlement.state", "sale_order_id.state",
        "object_id.invoice_lines.agents"
    )
    def _compute_settled(self):
        for line in self:
            agent_lines = [line]
            # consider both sale and invoice lines
            inv_lines = line.object_id.invoice_lines
            for inv_line in inv_lines:
                for inv_agent_line in inv_line.agents:
                    if inv_agent_line.agent.id == line.agent.id:
                        agent_lines.append(inv_agent_line)
            settlement_lines = self.env["sale.commission.settlement.line"]
            for agent_line in agent_lines:
                settlement_lines |= agent_line.agent_line
            line.settled = (any(
                x.settlement.state != "cancel" for x in settlement_lines
            ))
