# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    commission_ids = fields.Many2many(
        comodel_name="sale.commission",
        string="Commissions",
        related="agent_line.commission_ids",
    )
