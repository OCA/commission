from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    current_agent_total = fields.Float(
        string="My Commission",
        compute="_compute_current_agent_total",
        store=False,
    )

    @api.depends("order_line.agent_ids.amount")
    def _compute_current_agent_total(self):
        for record in self:
            my_com = record.mapped("order_line.agent_ids").filtered(
                lambda x: x.agent_id == self.env.user.partner_id
            )
            record.current_agent_total = sum(my_com.mapped("amount"))
