# Copyright 2023 Nextev
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields

from .common import TestPartialSettlementCommon


class TestPartialSettlement(TestPartialSettlementCommon):
    def test_partial_payment_amount_settlement(self):
        sale_order = self._create_multi_line_sale_order(
            self.agent_monthly, self.partial_commission_net_paid
        )
        sale_order.action_confirm()
        date = fields.Date.today()
        invoice = self._invoice_sale_order(sale_order)
        partial_amount = invoice.amount_total / 3
        self.register_payment(
            invoice,
            date + relativedelta(days=-2),
            amount=partial_amount,
            payment_difference_handling="open",
        )
        self.assertTrue(invoice._get_reconciled_invoices_partials())
        self._settle_agent(self.agent_monthly, 1, datetime.now())
        settlements = self.env["commission.settlement"].search(
            [
                (
                    "agent_id",
                    "=",
                    self.agent_monthly.id,
                ),
                ("state", "=", "settled"),
            ]
        )
        self.assertEqual(1, len(settlements))
        self.assertEqual(2, len(settlements.line_ids))
        self.assertEqual(2, len(invoice.line_ids.agent_ids))

    def test_multi_agents_settlement(self):
        agent_net = self.agent_biweekly
        commission_net = self.commission_net_invoice
        agent_partial = self.agent_monthly
        commission_partial = self.partial_commission_net_paid
        sale_order = self._create_multi_line_sale_order(agent_net, commission_net)
        sale_order.action_confirm()
        invoice = self._invoice_sale_order(sale_order)
        invoice.action_post()
        sale_order2 = self._create_multi_line_sale_order(
            agent_partial, commission_partial
        )
        sale_order2.action_confirm()
        invoice2 = self._invoice_sale_order(sale_order2)
        self.register_payment(
            invoice2,
            fields.Date.today() + relativedelta(days=-2),
        )
        self._settle_agent(period=1)
        settlements = self.settle_model.search(
            [("agent_id", "in", [agent_net.id, agent_partial.id])]
        )
        self.assertEqual(len(settlements), 2)
