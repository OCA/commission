# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2022 Quartile
# Copyright 2016-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.fields import Command
from odoo.tests import Form, tagged

from odoo.addons.account_commission_oca.tests.test_account_commission import (
    TestAccountCommission,
)


@tagged("post_install", "-at_install")
class TestSaleCommission(TestAccountCommission):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.product.write({"invoice_policy": "order"})

    def _create_sale_order(self, agent, commission):
        order_form = Form(self.sale_order_model)
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        order = order_form.save()
        order.order_line.agent_ids = [
            Command.create({"agent_id": agent.id, "commission_id": commission.id})
        ]
        return order

    def _invoice_sale_order(self, sale_order, date=None):
        old_invoices = sale_order.invoice_ids
        wizard = self.advance_inv_model.create(
            {
                "advance_payment_method": "delivered",
                "sale_order_ids": [Command.link(sale_order.id)],
            }
        )
        wizard.create_invoices()
        invoice = sale_order.invoice_ids - old_invoices
        if date:
            invoice.invoice_date = date
            invoice.date = date
        return

    def _create_order_and_invoice(self, agent, commission):
        sale_order = self._create_sale_order(agent, commission)
        sale_order.action_confirm()
        self._invoice_sale_order(sale_order)
        invoices = sale_order.invoice_ids
        invoices.invoice_line_ids.agent_ids._compute_amount()
        return sale_order

    def _create_order_refund(self, sale_order, agent, commission):
        refund = self.env["account.move"].create(
            {
                "move_type": "out_refund",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "sale_line_ids": [Command.set(sale_order.order_line.ids)],
                            "agent_ids": [
                                Command.create(
                                    {
                                        "agent_id": agent.id,
                                        "commission_id": commission.id,
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        )
        return refund.invoice_line_ids.agent_ids

    def _check_full(self, agent, commission, period, initial_count):
        sale_order = self._create_order_and_invoice(agent, commission)
        settlements = self._check_invoice_thru_settle(
            agent, commission, period, initial_count, sale_order
        )
        return settlements

    def test_sale_commission_gross_amount_payment(self):
        self._check_full(
            self.agent_monthly,
            self.commission_section_paid,
            1,
            0,
        )

    def test_sale_commission_status(self):
        # Make sure user is in English
        self.env.user.lang = "en_US"
        sale_order = self._create_sale_order(
            self.agent_monthly,
            self.commission_section_invoice,
        )
        self.assertIn("1", sale_order.order_line[0].commission_status)
        self.assertNotIn("agents", sale_order.order_line[0].commission_status)
        sale_order.mapped("order_line.agent_ids").unlink()
        self.assertIn("No", sale_order.order_line[0].commission_status)
        sale_order.order_line[0].agent_ids = [
            Command.create(
                {
                    "agent_id": self.agent_monthly.id,
                    "commission_id": self.commission_section_invoice.id,
                }
            ),
            Command.create(
                {
                    "agent_id": self.agent_quaterly.id,
                    "commission_id": self.commission_section_invoice.id,
                },
            ),
        ]
        self.assertIn("2", sale_order.order_line[0].commission_status)
        self.assertIn("agents", sale_order.order_line[0].commission_status)
        # Free
        sale_order.order_line.commission_free = True
        self.assertIn("free", sale_order.order_line.commission_status)
        self.assertAlmostEqual(sale_order.order_line.agent_ids.amount, 0)
        # test show agents buton
        action = sale_order.order_line.button_edit_agents()
        self.assertEqual(action["res_id"], sale_order.order_line.id)

    def test_sale_commission_propagation(self):
        self.partner.commission_agent_ids = [(4, self.agent_monthly.id)]
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 1
        sale_order = sale_order_form.save()
        agent = sale_order.order_line.agent_ids
        self._check_propagation(agent, self.commission_net_invoice, self.agent_monthly)
        # Check agent change
        agent.agent_id = self.agent_quaterly
        self.assertTrue(agent.commission_id, self.commission_section_invoice)
        # Check recomputation
        agent.unlink()
        sale_order.recompute_lines_agents()
        agent = sale_order.order_line.agent_ids
        self._check_propagation(agent, self.commission_net_invoice, self.agent_monthly)

    def test_sale_commission_invoice_line_agent(self):
        sale_order = self._create_sale_order(
            self.agent_monthly,
            self.commission_section_invoice,
        )
        sale_order.action_confirm()
        self._invoice_sale_order(sale_order)
        inv_line = sale_order.mapped("invoice_ids.invoice_line_ids")[0]
        self.assertTrue(
            inv_line.agent_ids[0].commission_id, self.commission_section_invoice
        )
        self.assertTrue(inv_line.agent_ids[0].agent_id, self.agent_monthly)

    def test_refund_from_order_refunded_agent_lines(self):
        """A credit note reversing no invoice refunds the latest posted invoice
        of its order lines, or the order lines when not invoiced yet."""
        agent = self.agent_monthly
        commission = self.commission_net_invoice
        sale_order = self._create_sale_order(agent, commission)
        sale_order.action_confirm()
        agent_line = self._create_order_refund(sale_order, agent, commission)
        self.assertEqual(
            agent_line._get_refunded_agent_lines(commission),
            sale_order.order_line.agent_ids,
        )
        agent_line.invoice_id.unlink()
        self._invoice_sale_order(sale_order)
        invoice = sale_order.invoice_ids
        invoice.action_post()
        agent_line = self._create_order_refund(sale_order, agent, commission)
        self.assertEqual(
            agent_line._get_refunded_agent_lines(commission),
            invoice.invoice_line_ids.agent_ids,
        )
