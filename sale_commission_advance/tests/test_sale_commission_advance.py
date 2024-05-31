import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestSaleCommission(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["commission"]
        cls.res_partner_model = cls.env["res.partner"]
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.commission_1 = cls.commission_model.create(
            {
                "name": "10% fixed commission",
                "fix_qty": 10.0,
                "commission_type": "fixed",
                "amount_base_type": "gross_amount",
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_5")
        cls.product_2 = cls.env.ref("product.product_product_6")
        cls.product_1.write({"invoice_policy": "order"})
        cls.product_2.write({"invoice_policy": "order"})
        cls.agent_1 = cls.res_partner_model.create(
            {
                "name": "Test Agent 1",
                "agent": True,
                "lang": "en_US",
                "settlement": "monthly",
                "commission_id": cls.commission_1.id,
            }
        )
        cls.agent_2 = cls.res_partner_model.create(
            {
                "name": "Test Agent 2",
                "agent": True,
                "lang": "en_US",
                "settlement": "monthly",
                "commission_id": cls.commission_1.id,
            }
        )
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.agent_ids = [(6, 0, (cls.agent_1 + cls.agent_2).ids)]
        cls.default_account_revenue = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.env.company[0].id),
                ("account_type", "=", "income"),
            ],
            limit=1,
        )

    def _create_sale_order(self):
        return self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_1.name,
                            "product_id": self.product_1.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": 500,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product_2.name,
                            "product_id": self.product_2.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": 500,
                        },
                    ),
                ],
            }
        )

    def _invoice_sale_order(self, sale_order, date=None, method="percentage"):
        old_invoices = sale_order.invoice_ids
        if method == "delivered":
            wizard = self.advance_inv_model.create(
                {
                    "advance_payment_method": method,
                    "sale_order_ids": sale_order.ids,
                }
            )
        else:
            wizard = self.advance_inv_model.create(
                {
                    "advance_payment_method": method,
                    "amount": 10,
                    "deposit_account_id": self.default_account_revenue.id,
                    "sale_order_ids": sale_order.ids,
                }
            )
        wizard.create_invoices()
        invoice = sale_order.invoice_ids - old_invoices
        if date:
            invoice.invoice_date = date
            invoice.date = date
        # We need to use flush() in order to execute commission_amount
        invoice.flush_recordset()
        return invoice

    def test_down_payment_flow(self):
        # Sale order
        order_id = self._create_sale_order()
        order_id._compute_commission_total()
        self.assertEqual(order_id.commission_total, 200)
        self.assertEqual(len(order_id.order_line.agent_ids), 4)
        order_id.order_line[0].agent_ids[1].unlink()
        order_id.order_line[1].agent_ids[1].unlink()
        self.assertEqual(order_id.commission_total, 100)
        self.assertEqual(len(order_id.order_line.agent_ids), 2)
        order_id.action_confirm()
        # Down Payment Invoice
        dp_invoice_id = self._invoice_sale_order(order_id)
        self.assertEqual(dp_invoice_id.commission_total, 10)
        self.assertEqual(len(dp_invoice_id.invoice_line_ids.agent_ids), 1)
        # Regular Invoice
        invoice_id = self._invoice_sale_order(order_id, method="delivered")
        self.assertEqual(invoice_id.commission_total, 90)
        dp_sol_id = order_id.order_line[0]
        self.assertEqual(len(dp_sol_id.agent_ids), 1)

    def test_regular_flow(self):
        # Sale order
        order_id = self._create_sale_order()
        order_id._compute_commission_total()
        self.assertEqual(order_id.commission_total, 200)
        self.assertEqual(len(order_id.order_line.agent_ids), 4)
        order_id.action_confirm()
        # Regular Invoice
        invoice_id = self._invoice_sale_order(order_id, method="delivered")
        self.assertEqual(invoice_id.commission_total, 200)
        self.assertEqual(len(invoice_id.invoice_line_ids.agent_ids), 4)
