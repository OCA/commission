from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.partner_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        down_payment_items = self.filtered(
            lambda x: x.order_id.partner_id and x.is_downpayment
        )
        for record in down_payment_items:
            agent_ids = record._prepare_agents_vals_partner_down_payment(
                record.order_id.partner_id
            )
            record.update({"agent_ids": agent_ids})
        regular_items = self - down_payment_items
        if regular_items:
            super(SaleOrderLine, regular_items)._compute_agent_ids()

    def _prepare_agents_vals_partner_down_payment(self, partner):
        res = []
        if self.invoice_lines:
            for agent_id in partner.agent_ids:
                for line in self.invoice_lines:
                    if (
                        line.agent_ids
                        and agent_id.id in line.agent_ids.mapped("agent_id").ids
                    ):
                        res.append(
                            (
                                0,
                                0,
                                {
                                    "agent_id": agent_id.id,
                                    "amount": 0,
                                    "commission_id": agent_id.commission_id.id,
                                },
                            )
                        )
        return res
