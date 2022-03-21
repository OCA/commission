# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestCommissionFormula(TransactionCase):
    def setUp(self):
        super(TestCommissionFormula, self).setUp()
        self.partner = self.env.ref("base.res_partner_2")
        self.advance_inv_model = self.env["sale.advance.payment.inv"]
        self.commission_agentprice = self.env["sale.commission"].create(
            {"name": "Agent price", "commission_type": "supplierinfo", "active": True}
        )
        self.agent = self.env["res.partner"].create(
            {
                "name": "Agent 0",
                "agent": True,
                "is_company": True,
                "supplier_rank": 1,
                "customer_rank": 0,
                "commission_id": self.commission_agentprice.id,
            }
        )
        self.seller = self.env["product.supplierinfo"].create(
            {"name": self.agent.id, "price": 30.0}
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Demo",
                "standard_price": 35.0,
                "seller_ids": [(6, 0, [self.seller.id])],
                "type": "consu",
                "default_code": "PROD_DEL01",
            }
        )
        self.sale_order = self.env["sale.order"].create(
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
                            "price_unit": self.product.standard_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": self.agent.id,
                                        "commission_id": self.commission_agentprice.id,
                                    },
                                )
                            ],
                        },
                    )
                ],
            }
        )
        self.so_line = self.sale_order.order_line

    def _invoice_sale_order(self, sale_order):
        wizard = self.advance_inv_model.create({"advance_payment_method": "delivered"})
        wizard.with_context(
            {
                "active_model": "sale.order",
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
            }
        ).create_invoices()

    def test_sale_order_commission(self):
        # testing the 'supplierinfo' commission
        # since the agent product price is 30 and the product quantity is 1,
        # the order total amount is 30.00.
        self.so_line.agent_ids = False  # Erase current agents
        self.env["sale.order.line.agent"].create(
            {
                "object_id": self.so_line.id,
                "agent_id": self.agent.id,
                "commission_id": self.commission_agentprice.id,
            }
        )
        self.assertEqual(30, self.sale_order.commission_total)

    def test_invoice_commission(self):
        self.sale_order.action_confirm()
        self.so_line.qty_delivered = self.so_line.product_uom_qty
        self._invoice_sale_order(self.sale_order)
        self.sale_order.invoice_ids.post()
        invoice = self.sale_order.invoice_ids[0]
        # adding the commissions on the first invoice line
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line.agent_ids = False  # Erase current agents
        self.env["account.invoice.line.agent"].create(
            {
                "object_id": invoice_line.id,
                "agent_id": self.agent.id,
                "commission_id": self.commission_agentprice.id,
            }
        )
        # testing the 'supplierinfo' commissions on the invoice too
        self.assertEqual(30, invoice.commission_total)

    def test_invoice_refund_commission(self):
        self.sale_order.action_confirm()
        self.so_line.qty_delivered = self.so_line.product_uom_qty
        self._invoice_sale_order(self.sale_order)
        self.sale_order.invoice_ids.post()
        invoice = self.sale_order.invoice_ids[0]
        # adding the commissions on the first invoice line
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line.agent_ids = False  # Erase current agents
        self.env["account.invoice.line.agent"].create(
            {
                "object_id": invoice_line.id,
                "agent_id": self.agent.id,
                "commission_id": self.commission_agentprice.id,
            }
        )
        # testing the 'supplierinfo' commissions on the invoice too
        self.assertEqual(30, invoice.commission_total)
        reverse = invoice._reverse_moves(cancel=True)
        self.assertEqual(-30, reverse.commission_total)
