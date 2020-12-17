# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

import dateutil.relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, SavepointCase


class TestSaleCommission(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["sale.commission"]
        cls.commission_net_paid = cls.commission_model.create(
            {
                "name": "20% fixed commission (Net amount) - Payment Based",
                "fix_qty": 20.0,
                "invoice_state": "paid",
                "amount_base_type": "net_amount",
            }
        )
        cls.commission_net_invoice = cls.commission_model.create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )
        cls.commission_section_paid = cls.commission_model.create(
            {
                "name": "Section commission - Payment Based",
                "commission_type": "section",
                "invoice_state": "paid",
                "section_ids": [
                    (0, 0, {"amount_from": 1.0, "amount_to": 100.0, "percent": 10.0})
                ],
                "amount_base_type": "net_amount",
            }
        )
        cls.commission_section_invoice = cls.commission_model.create(
            {
                "name": "Section commission - Invoice Based",
                "commission_type": "section",
                "section_ids": [
                    (
                        0,
                        0,
                        {
                            "amount_from": 15000.0,
                            "amount_to": 16000.0,
                            "percent": 20.0,
                        },
                    )
                ],
            }
        )
        cls.company = cls.env.ref("base.main_company")
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.write({"agent": False})
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.settle_model = cls.env["sale.commission.settlement"]
        cls.make_settle_model = cls.env["sale.commission.make.settle"]
        cls.make_inv_model = cls.env["sale.commission.make.invoice"]
        cls.product = cls.env.ref("product.product_product_5")
        cls.product.list_price = 5  # for testing specific commission section
        cls.commission_product = cls.env["product.product"].create(
            {"name": "Commission test product", "type": "service"}
        )
        cls.product.write({"invoice_policy": "order"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        cls.agent_monthly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Monthly",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
                "commission_id": cls.commission_net_invoice.id,
            }
        )
        cls.agent_quaterly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Quaterly",
                "agent": True,
                "settlement": "quaterly",
                "lang": "en_US",
                "commission_id": cls.commission_section_invoice.id,
            }
        )
        cls.agent_semi = cls.res_partner_model.create(
            {
                "name": "Test Agent - Semi-annual",
                "agent": True,
                "settlement": "semi",
                "lang": "en_US",
            }
        )
        cls.agent_annual = cls.res_partner_model.create(
            {
                "name": "Test Agent - Annual",
                "agent": True,
                "settlement": "annual",
                "lang": "en_US",
            }
        )
        cls.income_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("user_type_id.name", "=", "Income"),
            ],
            limit=1,
        )

    def _create_sale_order(self, agent, commission):
        return self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": self.product.lst_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": agent.id,
                                        "commission_id": commission.id,
                                    },
                                )
                            ],
                        },
                    )
                ],
            }
        )

    def _invoice_sale_order(self, sale_order):
        wizard = self.advance_inv_model.create({"advance_payment_method": "delivered"})
        wizard.with_context(
            {
                "active_model": "sale.order",
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
            }
        ).create_invoices()

    def _settle_agent(self, agent, period):
        vals = {
            "date_to": (
                fields.Datetime.from_string(fields.Datetime.now())
                + dateutil.relativedelta.relativedelta(months=period)
            ),
        }
        if agent:
            vals["agent_ids"] = [(4, agent.id)]
        wizard = self.make_settle_model.create(vals)
        wizard.action_settle()

    def _create_order_and_invoice_and_settle(self, agent, commission, period):
        sale_order = self._create_sale_order(agent, commission)
        sale_order.action_confirm()
        self._invoice_sale_order(sale_order)
        invoices = sale_order.invoice_ids
        invoices.invoice_line_ids.agent_ids._compute_amount()
        invoices.action_post()
        self._settle_agent(agent, period)
        return sale_order

    def _check_full(self, agent, commission, period, initial_count):
        sale_order = self._create_order_and_invoice_and_settle(
            agent, commission, period
        )
        settlements = self.settle_model.search([("state", "=", "settled")])
        self.assertEqual(len(settlements), initial_count)
        journal = self.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", sale_order.company_id.id)],
            limit=1,
        )
        register_payments = (
            self.env["account.payment.register"]
            .with_context(
                active_ids=sale_order.invoice_ids.id, active_model="account.move"
            )
            .create({"journal_id": journal.id})
        )
        register_payments.action_create_payments()
        self.assertEqual(sale_order.invoice_ids.payment_state, "paid")
        self._settle_agent(agent, period)
        settlements = self.settle_model.search([("state", "=", "settled")])
        self.assertTrue(settlements)
        inv_line = sale_order.mapped("invoice_ids.invoice_line_ids")[0]
        self.assertTrue(inv_line.any_settled)
        with self.assertRaises(ValidationError):
            inv_line.agent_ids.amount = 5
        settlements.make_invoices(self.journal, self.commission_product)
        for settlement in settlements:
            self.assertEqual(settlement.state, "invoiced")
        with self.assertRaises(UserError):
            settlements.action_cancel()
        with self.assertRaises(UserError):
            settlements.unlink()
        return settlements

    def test_sale_commission_gross_amount_payment(self):
        settlements = self._check_full(
            self.env.ref("sale_commission.res_partner_pritesh_sale_agent"),
            self.commission_section_paid,
            1,
            0,
        )
        # Check report print - It shouldn't fail
        self.env.ref("sale_commission.action_report_settlement")._render_qweb_html(
            settlements[0].ids
        )

    def test_sale_commission_gross_amount_payment_annual(self):
        self._check_full(self.agent_annual, self.commission_section_paid, 12, 0)

    def test_sale_commission_gross_amount_payment_semi(self):
        self.product.list_price = 15100  # for testing specific commission section
        self._check_full(self.agent_semi, self.commission_section_invoice, 6, 1)

    def test_sale_commission_gross_amount_invoice(self):
        self._create_order_and_invoice_and_settle(
            self.agent_quaterly,
            self.env.ref("sale_commission.demo_commission"),
            1,
        )
        settlements = self.settle_model.search([("state", "=", "invoiced")])
        settlements.make_invoices(self.journal, self.commission_product)
        for settlement in settlements:
            self.assertNotEqual(
                len(settlement.invoice_id),
                0,
                "Settlements need to be in Invoiced State.",
            )

    def test_wrong_section(self):
        with self.assertRaises(ValidationError):
            self.commission_model.create(
                {
                    "name": "Section commission - Invoice Based",
                    "commission_type": "section",
                    "section_ids": [
                        (0, 0, {"amount_from": 5, "amount_to": 1, "percent": 20.0})
                    ],
                }
            )

    def test_commission_status(self):
        # Make sure user is in English
        self.env.user.lang = "en_US"
        sale_order = self._create_sale_order(
            self.env.ref("sale_commission.res_partner_pritesh_sale_agent"),
            self.commission_section_invoice,
        )
        self.assertIn("1", sale_order.order_line[0].commission_status)
        self.assertNotIn("agents", sale_order.order_line[0].commission_status)
        sale_order.mapped("order_line.agent_ids").unlink()
        self.assertIn("No", sale_order.order_line[0].commission_status)
        sale_order.order_line[0].agent_ids = [
            (
                0,
                0,
                {
                    "agent_id": self.env.ref(
                        "sale_commission.res_partner_pritesh_sale_agent"
                    ).id,
                    "commission_id": self.env.ref("sale_commission.demo_commission").id,
                },
            ),
            (
                0,
                0,
                {
                    "agent_id": self.env.ref(
                        "sale_commission.res_partner_eiffel_sale_agent"
                    ).id,
                    "commission_id": self.env.ref("sale_commission.demo_commission").id,
                },
            ),
        ]
        self.assertIn("2", sale_order.order_line[0].commission_status)
        self.assertIn("agents", sale_order.order_line[0].commission_status)
        sale_order.action_confirm()
        wizard = self.advance_inv_model.create({"advance_payment_method": "delivered"})
        wizard.with_context(
            {
                "active_model": "sale.order",
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
            }
        ).create_invoices()
        invoice = sale_order.invoice_ids
        self.assertIn("2", invoice.invoice_line_ids[0].commission_status)
        self.assertIn("agents", invoice.invoice_line_ids[0].commission_status)
        # Free
        sale_order.order_line.commission_free = True
        self.assertIn("free", sale_order.order_line.commission_status)
        self.assertAlmostEqual(sale_order.order_line.agent_ids.amount, 0)
        invoice.invoice_line_ids.commission_free = True
        self.assertIn("free", invoice.invoice_line_ids.commission_status)
        self.assertAlmostEqual(invoice.invoice_line_ids.agent_ids.amount, 0)
        # test show agents buton
        action = sale_order.order_line.button_edit_agents()
        self.assertEqual(action["res_id"], sale_order.order_line.id)

    def test_supplier_invoice(self):
        """No agents should be populated on supplier invoices."""
        self.partner.agent_ids = self.agent_semi
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        move_form.partner_id = self.partner
        move_form.ref = "sale_comission_TEST"
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.quantity = 1
            line_form.currency_id = self.company.currency_id
        invoice = move_form.save()
        self.assertFalse(invoice.invoice_line_ids.agent_ids)

    def _check_propagation(self, agent):
        self.assertTrue(agent)
        self.assertTrue(agent.commission_id, self.commission_net_invoice)
        self.assertTrue(agent.agent_id, self.agent_monthly)

    def test_commission_propagation(self):
        """Test propagation of agents from partner to SO/invoice and SO>invoice."""
        self.partner.agent_ids = [(4, self.agent_monthly.id)]
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 1
        sale_order = sale_order_form.save()
        agent = sale_order.order_line.agent_ids
        self._check_propagation(agent)
        # Check agent change
        agent.agent_id = self.agent_quaterly
        self.assertTrue(agent.commission_id, self.commission_section_invoice)
        # HACK: Remove constraints as in test mode it raises, but not on regular UI
        # TODO: Check why this is happening only in tests
        self.env.cr.execute(
            "ALTER TABLE sale_order_line_agent DROP CONSTRAINT "
            "sale_order_line_agent_unique_agent"
        )
        self.env.cr.execute(
            "ALTER TABLE account_invoice_line_agent DROP CONSTRAINT "
            "account_invoice_line_agent_unique_agent"
        )
        # Check recomputation
        agent.unlink()
        sale_order.recompute_lines_agents()
        self._check_propagation(sale_order.order_line.agent_ids)
        sale_order.action_confirm()
        self._invoice_sale_order(sale_order)
        agent = sale_order.invoice_ids.invoice_line_ids.agent_ids
        self._check_propagation(agent)
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.currency_id = self.company.currency_id
            line_form.product_id = self.product
            line_form.quantity = 1
        invoice = move_form.save()
        agent = invoice.invoice_line_ids.agent_ids
        self._check_propagation(agent)
        # Check agent change
        agent.agent_id = self.agent_quaterly
        self.assertTrue(agent.commission_id, self.commission_section_invoice)
        # Check recomputation
        agent.unlink()
        invoice.recompute_lines_agents()
        self._check_propagation(invoice.invoice_line_ids.agent_ids)

    def test_negative_settlements(self):
        self.product.write({"list_price": 1000})
        agent = self.agent_monthly
        commission = self.commission_net_invoice
        sale_order = self._create_order_and_invoice_and_settle(agent, commission, 1)
        settlement = self.settle_model.search([("agent_id", "=", agent.id)])
        self.assertEqual(1, len(settlement))
        self.assertEqual(settlement.state, "settled")
        commission_invoice = settlement.make_invoices(
            product=self.commission_product, journal=self.journal
        )
        self.assertEqual(settlement.state, "invoiced")
        self.assertEqual(commission_invoice.move_type, "in_invoice")
        invoice = sale_order.invoice_ids
        refund = invoice._reverse_moves(
            default_values_list=[{"invoice_date": invoice.invoice_date}],
        )
        self.assertEqual(
            invoice.invoice_line_ids.agent_ids.agent_id,
            refund.invoice_line_ids.agent_ids.agent_id,
        )
        refund.invoice_line_ids.agent_ids._compute_amount()
        refund.action_post()
        self._settle_agent(agent, 1)
        settlements = self.settle_model.search([("agent_id", "=", agent.id)])
        self.assertEqual(2, len(settlements))
        second_settlement = settlements.filtered(lambda r: r.total < 0)
        self.assertEqual(second_settlement.state, "settled")
        # Use invoice wizard for testing also this part
        wizard = self.env["sale.commission.make.invoice"].create(
            {"product_id": self.commission_product.id}
        )
        action = wizard.button_create()
        commission_refund = self.env["account.move"].browse(action["domain"][0][2])
        self.assertEqual(second_settlement.state, "invoiced")
        self.assertEqual(commission_refund.move_type, "in_refund")
        # Undo invoices + make invoice again to get a unified invoice
        commission_invoices = commission_invoice + commission_refund
        commission_invoices.button_cancel()
        self.assertEqual(settlement.state, "except_invoice")
        self.assertEqual(second_settlement.state, "except_invoice")
        commission_invoices.unlink()
        settlements.unlink()
        self._settle_agent(False, 1)  # agent=False for testing default
        settlement = self.settle_model.search([("agent_id", "=", agent.id)])
        # Check make invoice wizard
        action = settlement.action_invoice()
        self.assertEqual(action["context"]["settlement_ids"], settlement.ids)
        # Use invoice wizard for testing also this part
        wizard = self.env["sale.commission.make.invoice"].create(
            {
                "product_id": self.commission_product.id,
                "journal_id": self.journal.id,
                "settlement_ids": [(4, settlement.id)],
            }
        )
        action = wizard.button_create()
        invoice = self.env["account.move"].browse(action["domain"][0][2])
        self.assertEqual(invoice.move_type, "in_invoice")
        self.assertAlmostEqual(invoice.amount_total, 0)

    def test_res_partner_agent_propagation(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test partner",
                "agent_ids": [(4, self.agent_monthly.id), (4, self.agent_quaterly.id)],
            }
        )
        # Create
        child = self.env["res.partner"].create(
            {"name": "Test child", "parent_id": partner.id}
        )
        self.assertEqual(set(child.agent_ids.ids), set(partner.agent_ids.ids))
        # Write
        partner.agent_ids = [(4, self.agent_monthly.id)]
        self.assertEqual(set(child.agent_ids.ids), set(partner.agent_ids.ids))
