from odoo import models, fields, api


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    agent_sale_line = fields.Many2many(
        comodel_name="sale.order.line.agent",
        relation="settlement_agent_sale_line_rel", column1="settlement_id",
        column2="agent_sale_line_id", required=True)
    date = fields.Date(
        compute="_compute_date", store=True, related=False, string="Date")
    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line", store=True,
        related="agent_sale_line.object_id", string="Sale order line")
    order_id = fields.Many2one(
        comodel_name="sale.order", store=True, string="Order",
        related="sale_line_id.order_id")
    agent = fields.Many2one(
        comodel_name="res.partner", readonly=True, compute="_compute_agent",
        store=True, related=False)
    settled_amount = fields.Monetary(
        compute="_compute_settled_amount", readonly=True, store=True, related=False)
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_currency_id", store=True, readonly=True, related=False
    )
    commission = fields.Many2one(
        comodel_name="sale.commission", compute="_compute_commission", related=False)

    @api.depends("agent_sale_line.order_date", "agent_line.invoice_date")
    def _compute_date(self):
        for line in self:
            if line.agent_line:
                line.date = line.agent_line[0].invoice_date
            elif line.agent_sale_line:
                line.date = line.agent_sale_line[0].order_date.date()

    @api.depends("agent_sale_line.agent", "agent_line.agent")
    def _compute_agent(self):
        for line in self:
            if line.agent_line:
                line.agent = line.agent_line[0].agent.id
            elif line.agent_sale_line:
                line.agent = line.agent_sale_line[0].agent.id

    @api.depends("agent_sale_line.amount", "agent_line.amount")
    def _compute_settled_amount(self):
        # compute currency, otherwise monetary field gets
        # "'_unknown' object has no attribute 'round'"
        for line in self:
            if line.agent_line:
                line.settled_amount = line.agent_line[0].amount
            elif line.agent_sale_line:
                line.settled_amount = line.agent_sale_line[0].amount

    @api.depends("agent_sale_line.currency_id", "agent_line.currency_id")
    def _compute_currency_id(self):
        for line in self:
            if line.agent_line:
                line.currency_id = line.agent_line[0].currency_id.id
            elif line.agent_sale_line:
                line.currency_id = line.agent_sale_line[0].currency_id.id

    @api.depends("agent_sale_line.commission", "agent_line.commission")
    def _compute_commission(self):
        for line in self:
            if line.agent_line:
                line.commission = line.agent_line[0].commission.id
            elif line.agent_sale_line:
                line.commission = line.agent_sale_line[0].commission.id
