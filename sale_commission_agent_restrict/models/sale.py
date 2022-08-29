#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    current_agent_total = fields.Float(
        string="My Commission",
        compute="_compute_commission_total",
        store=True,
    )

    @api.depends("order_line.agents.amount")
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = sum(record.mapped("order_line.agents.amount"))
            my_com = record.mapped("order_line.agents").filtered(
                lambda x: x.agent == self.env.user.partner_id
            )
            record.current_agent_total = sum(my_com.mapped("amount"))
