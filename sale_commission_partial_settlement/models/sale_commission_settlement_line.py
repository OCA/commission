from odoo import api, fields, models


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    agent_line_partial_ids = fields.Many2many(
        comodel_name="account.invoice.line.agent.partial",
        relation="settlement_agent_line_partial_rel",
        column1="settlement_id",
        column2="agent_line_partial_id",
    )  # Deprecated, left for compatibility with previous versions
    settlement_line_partial_ids = fields.Many2many(
        comodel_name="sale.commission.settlement.line.partial",
        relation="settlement_line_line_partial_rel",
    )
    settled_amount = fields.Monetary(
        compute="_compute_settled_amount",
        related=False,
        readonly=True,
        store=True,
    )

    @api.depends("commission_id.payment_amount_type")
    def _compute_settled_amount(self):
        for rec in self:
            if rec.commission_id.payment_amount_type == "paid":
                if rec.settlement_line_partial_ids:
                    rec.settled_amount = sum(
                        x.amount for x in rec.settlement_line_partial_ids
                    )
                else:  # compatibility with previous versions
                    rec.settled_amount = rec.agent_line_partial_ids[:1].amount
            else:
                rec.settled_amount = rec.agent_line[:1].amount
