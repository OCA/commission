from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_partner_for_commission(self):
        return self.order_id.partner_id

    @api.depends("order_id.partner_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        down_payment_items = self.filtered(
            lambda x: x._get_partner_for_commission() and x.is_downpayment
        )
        for record in down_payment_items:
            agent_ids = record._prepare_agents_vals_partner_down_payment(
                record._get_partner_for_commission()
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
