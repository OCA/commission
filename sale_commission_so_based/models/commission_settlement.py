# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
from odoo import fields, models, api


class CommissionSettlement(models.Model):
    _inherit = "commission.settlement"

    settlement_type = fields.Selection(
        selection_add=[("sale_order", "Sales Orders")],
        ondelete={"sale_order": "set default"}
    )


class SettlementLine(models.Model):
    _inherit = "commission.settlement.line"

    sale_agent_line_id = fields.Many2one(comodel_name="sale.order.line.agent")
    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        store=True,
        related="sale_agent_line_id.object_id",
        string="Source invoice line",
    )

    @api.depends("invoice_agent_line_id", "sale_agent_line_id")
    def _compute_date(self):
        # pylint: disable= missing-return
        super()._compute_date()
        for record in self:
            if not record.sale_agent_line_id:
                continue
            record.date = record.sale_agent_line_id.invoice_date

    @api.depends("invoice_agent_line_id", "sale_agent_line_id")
    def _compute_commission_id(self):
        # pylint: disable= missing-return
        super()._compute_date()
        for record in self:
            if not record.sale_agent_line_id:
                continue
            record.commission_id = record.sale_agent_line_id.commission_id

    @api.depends("invoice_agent_line_id", "sale_agent_line_id")
    def _compute_settled_amount(self):
        # pylint: disable= missing-return
        super()._compute_date()
        for record in self:
            if not record.sale_agent_line_id:
                continue
            record.settled_amount = record.sale_agent_line_id.amount
