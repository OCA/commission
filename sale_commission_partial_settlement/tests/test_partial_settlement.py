# Copyright 2023 Nextev
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestPartialSettlement(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["sale.commission"]
        cls.partial_commission_net_paid = cls.commission_model.create(
            {
                "name": "20% fixed commission (Net amount) - Payment Based - Partial",
                "fix_qty": 20.0,
                "invoice_state": "paid",
                "amount_base_type": "net_amount",
                "payment_amount_type": "paid",
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
                "commission_id": cls.partial_commission_net_paid.id,
            }
        )
        cls.income_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("user_type_id.name", "=", "Income"),
            ],
            limit=1,
        )
        cls.commission_net_invoice = cls.commission_model.create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )
        cls.agent_biweekly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Bi-weekly",
                "agent": True,
                "settlement": "biweekly",
                "lang": "en_US",
                "commission_id": cls.commission_net_invoice.id,
            }
        )

    def _create_multi_line_sale_order(self, agent, commission):
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
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": self.product.lst_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": self.agent_monthly.id,
                                        "commission_id": self.partial_commission_net_paid.id,
                                    },
                                )
                            ],
                        },
                    ),
                ],
            }
        )

    def _invoice_sale_order(self, sale_order, date=None):
        old_invoices = sale_order.invoice_ids
        wizard = self.advance_inv_model.create({"advance_payment_method": "delivered"})
        wizard.with_context(
            {
                "active_model": "sale.order",
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
            }
        ).create_invoices()
        invoice = sale_order.invoice_ids - old_invoices
        invoice.flush()
        return invoice

    def _settle_agent(self, agent=None, period=None, date=None, date_payment_to=None):
        vals = {
            "date_to": (
                fields.Datetime.from_string(fields.Datetime.now())
                + relativedelta(months=period)
            )
            if period
            else date,
            "date_payment_to": date_payment_to,
        }
        if agent:
            vals["agent_ids"] = [(4, agent.id)]
        wizard = self.make_settle_model.create(vals)
        wizard.action_settle()

    def register_payment(
        self,
        invoice,
        payment_date,
        amount=None,
        payment_difference_handling="reconcile",
    ):
        payment_model = self.env["account.payment.register"]
        invoice.action_post()
        if not amount:
            amount = invoice.amount_total
        ctx = {
            "active_model": "account.move",
            "active_ids": [invoice.id],
        }
        return (
            payment_model.with_context(ctx)
            .create(
                {
                    "payment_date": payment_date,
                    "amount": amount,
                    "journal_id": self.env["account.journal"]
                    .search([("type", "=", "bank")], limit=1)
                    .id,
                    "payment_method_id": self.env.ref(
                        "account.account_payment_method_manual_out"
                    ).id,
                    "payment_difference_handling": payment_difference_handling,
                }
            )
            .action_create_payments()
        )

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
        self._settle_agent(self.agent_monthly, 1, date_payment_to=datetime.now())
        settlements = self.env["sale.commission.settlement"].search(
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

    def test_skip_partial_future_payment(self):
        sale_order = self._create_multi_line_sale_order(
            self.agent_monthly, self.partial_commission_net_paid
        )
        sale_order.action_confirm()
        date = fields.Date.today()
        invoice = self._invoice_sale_order(sale_order)
        self.register_payment(
            invoice,
            date + relativedelta(days=2),
        )
        self._settle_agent(self.agent_monthly, 1, date_payment_to=datetime.now())
        settlements = self.env["sale.commission.settlement"].search(
            [
                (
                    "agent_id",
                    "=",
                    self.agent_monthly.id,
                ),
                ("state", "=", "settled"),
            ]
        )
        self.assertEqual(0, len(settlements))

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
