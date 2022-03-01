from odoo import fields, models


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    commission_ids = fields.Many2many(
        comodel_name="sale.commission", related="agent_line.commission_ids"
    )
