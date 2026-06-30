# Copyright 2026 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestCommissionProductFixed(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls._create_product(name="Product A")
        cls.product_b = cls._create_product(name="Product B")
        cls.agent_x = cls.env["res.partner"].create({"name": "Agent X", "agent": True})
        cls.agent_y = cls.env["res.partner"].create({"name": "Agent Y", "agent": True})
        cls.commission_x = cls.env["commission"].create(
            {
                "name": "Agent X scheme",
                "commission_type": "product_fixed",
                "settlement_type": "sale_invoice",
                "product_line_ids": [
                    Command.create({"product_id": cls.product_a.id, "amount": 500}),
                    Command.create({"product_id": cls.product_b.id, "amount": 300}),
                ],
            }
        )
        cls.commission_y = cls.env["commission"].create(
            {
                "name": "Agent Y scheme",
                "commission_type": "product_fixed",
                "settlement_type": "sale_invoice",
                "product_line_ids": [
                    Command.create({"product_id": cls.product_a.id, "amount": 650}),
                ],
            }
        )
        cls.customer = cls.partner_a

    def _create_invoice(
        self,
        agent,
        commission,
        product,
        qty,
        invoice_date=None,
        move_type="out_invoice",
    ):
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": self.customer.id,
                "invoice_date": invoice_date,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": qty,
                            "price_unit": 1000,
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

    def test_fixed_amount_times_quantity(self):
        invoice = self._create_invoice(
            self.agent_x, self.commission_x, self.product_a, 3
        )
        agent_line = invoice.invoice_line_ids.agent_ids
        # 500 (fixed) x 3 (qty), independent of the 1000 price.
        self.assertEqual(agent_line.amount, 1500)

    def test_amount_differs_by_agent(self):
        invoice_x = self._create_invoice(
            self.agent_x, self.commission_x, self.product_a, 1
        )
        invoice_y = self._create_invoice(
            self.agent_y, self.commission_y, self.product_a, 1
        )
        self.assertEqual(invoice_x.invoice_line_ids.agent_ids.amount, 500)
        self.assertEqual(invoice_y.invoice_line_ids.agent_ids.amount, 650)

    def test_post_blocked_when_amount_missing(self):
        # Agent Y has no amount defined for product B.
        invoice = self._create_invoice(
            self.agent_y, self.commission_y, self.product_b, 1
        )
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 0)
        with self.assertRaises(ValidationError):
            invoice.action_post()

    def test_post_allowed_when_amount_defined(self):
        invoice = self._create_invoice(
            self.agent_x, self.commission_x, self.product_b, 2
        )
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 600)

    def test_min_qty_tier(self):
        # Volume tier: above 10 units, product A grants 400 instead of 500.
        self.env["commission.product.line"].create(
            {
                "commission_id": self.commission_x.id,
                "product_id": self.product_a.id,
                "min_qty": 10,
                "amount": 400,
            }
        )
        below = self._create_invoice(self.agent_x, self.commission_x, self.product_a, 5)
        above = self._create_invoice(
            self.agent_x, self.commission_x, self.product_a, 12
        )
        self.assertEqual(below.invoice_line_ids.agent_ids.amount, 2500)  # 500 x 5
        self.assertEqual(above.invoice_line_ids.agent_ids.amount, 4800)  # 400 x 12

    def test_date_validity(self):
        # Restrict the product A amount to a window that excludes the invoice.
        self.commission_x.product_line_ids.filtered(
            lambda x: x.product_id == self.product_a
        ).write({"date_start": date(2026, 1, 1), "date_end": date(2026, 1, 31)})
        out_of_range = self._create_invoice(
            self.agent_x,
            self.commission_x,
            self.product_a,
            1,
            invoice_date=date(2026, 6, 1),
        )
        self.assertEqual(out_of_range.invoice_line_ids.agent_ids.amount, 0)
        with self.assertRaises(ValidationError):
            out_of_range.action_post()
        in_range = self._create_invoice(
            self.agent_x,
            self.commission_x,
            self.product_a,
            1,
            invoice_date=date(2026, 1, 15),
        )
        self.assertEqual(in_range.invoice_line_ids.agent_ids.amount, 500)

    def test_start_date_after_end_date(self):
        with self.assertRaises(ValidationError):
            self.env["commission.product.line"].create(
                {
                    "commission_id": self.commission_x.id,
                    "product_id": self.product_b.id,
                    "amount": 100,
                    "date_start": date(2026, 2, 1),
                    "date_end": date(2026, 1, 1),
                }
            )

    def test_refund_amount_is_negative(self):
        # On a refund the base _compute_amount negates the commission, so the
        # fixed amount must come out as -(amount x quantity).
        refund = self._create_invoice(
            self.agent_x,
            self.commission_x,
            self.product_a,
            3,
            move_type="out_refund",
        )
        # -(500 fixed x 3 qty), mirroring test_fixed_amount_times_quantity.
        self.assertEqual(refund.invoice_line_ids.agent_ids.amount, -1500)
