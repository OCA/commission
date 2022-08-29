#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    current_agent_total = fields.Float(
        string="My Commission",
        compute="_compute_current_agent_total",
    )

    @api.depends(
        "commission_total",
        "order_line.agents.agent",
    )
    def _compute_current_agent_total(self):
        current_partner = self.env.user.partner_id
        for order in self:
            my_com = order.mapped("order_line.agents").filtered(
                lambda x: x.agent == current_partner
            )
            order.current_agent_total = sum(my_com.mapped("amount"))
