from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        """
        _prepare_agents_vals_down_payment is called after _get_commission_amount on
        account.invoice.line.agent. Need to call _get_commission_amount again to apply
        custom amount calculation on down payment line. Otherwise, amount will be 0.
        """
        rec = super().create(vals)
        if rec.has_related_sale_with_down_payment():
            rec.recompute_lines_agents()
        return rec

    def has_related_sale_with_down_payment(self):
        return any(
            self.invoice_line_ids.mapped(
                lambda x: x.sale_line_ids and x.sale_line_ids.is_downpayment
            )
        )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id.partner_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        down_payment_items = self.filtered(
            lambda x: x.move_id.partner_id
            and x.move_id.move_type[:3] == "out"
            and x.sale_line_ids.is_downpayment
        )
        for record in down_payment_items:
            agent_ids = record._prepare_agents_vals_down_payment()
            record.update({"agent_ids": agent_ids})
        regular_items = self - down_payment_items
        if regular_items:
            super(AccountMoveLine, regular_items)._compute_agent_ids()

    def _prepare_agents_vals_partner(self, partner):
        if not self.move_id.has_related_sale_with_down_payment():
            return super()._prepare_agents_vals_partner(partner)
        sol_agents = self.sale_line_ids.mapped("agent_ids").filtered(
            lambda x: x.amount > 0
        )
        agent_ids = sol_agents.mapped("agent_id")
        res = []
        for agent_id in agent_ids:
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

    def _prepare_agents_vals_down_payment(self):
        # Add agent lines with amount > 0 and with total commission amount
        self.sale_line_ids.ensure_one()
        sale_order_id = self.sale_line_ids.order_id
        agent_sol_ids = sale_order_id.order_line.filtered(
            lambda x: x.is_downpayment is False and x.product_id and x.agent_ids
        )
        sol_agents = agent_sol_ids.mapped("agent_ids").filtered(lambda x: x.amount > 0)
        agent_ids = sol_agents.mapped("agent_id")
        res = []
        for agent_id in agent_ids:
            total = sum(
                sol_agents.filtered(lambda x: x.agent_id == agent_id).mapped("amount")
            )
            res.append(
                (
                    0,
                    0,
                    {
                        "agent_id": agent_id.id,
                        "amount": 0,
                        "downpayment_base_amount": total,
                        "commission_id": agent_id.commission_id.id,
                    },
                )
            )
        return res


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    downpayment_base_amount = fields.Monetary(
        copy=False, help="Total agent commission based on Sale Order"
    )

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        self.ensure_one()
        if self.object_id.sale_line_ids and self.object_id.sale_line_ids.is_downpayment:
            sale_order_id = self.object_id.sale_line_ids.order_id
            ratio = self.object_id.price_total / sale_order_id.amount_total
            return self.downpayment_base_amount * ratio
        else:
            return super(AccountInvoiceLineAgent, self)._get_commission_amount(
                commission, subtotal, product, quantity
            )
