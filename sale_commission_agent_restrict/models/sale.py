from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    current_agent_total = fields.Float(
        string="My Commission",
        compute="_compute_commission_total",
        store=True,
    )

    @api.depends("order_line.agent_ids.amount")
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = sum(record.mapped("order_line.agent_ids.amount"))
            my_com = record.mapped("order_line.agent_ids").filtered(
                lambda x: x.agent_id == self.env.user.partner_id
            )
            record.current_agent_total = sum(my_com.mapped("amount"))
