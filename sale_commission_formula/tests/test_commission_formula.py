# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase


class TestCommissionFormula(TransactionCase):
    def setUp(self):
        super(TestCommissionFormula, self).setUp()
        self.advance_inv_model = self.env["sale.advance.payment.inv"]
        self.agent = self.env.ref("sale_commission_formula.agent1")
        self.commission = self.env.ref(
            "sale_commission_formula.commission_5perc10extra"
        )
        self.sale_order = self.env.ref("sale_commission_formula.sale_order_1")
        self.so_line = self.env.ref("sale_commission_formula.sale_order_line_1")

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
        # we test the '5% + 10% extra' we should return 41.25 since
        # the order total amount is 750.00.
        self.so_line.agent_ids = False  # Erase current agents
        self.env["sale.order.line.agent"].create(
            {
                "object_id": self.so_line.id,
                "agent_id": self.agent.id,
                "commission_id": self.commission.id,
            }
        )
        self.assertEqual(41.25, self.sale_order.commission_total)

    def test_invoice_commission(self):
        # we confirm the sale order and create the corresponding invoice
        self.sale_order.action_confirm()
        self.so_line.qty_delivered = self.so_line.product_uom_qty
        self._invoice_sale_order(self.sale_order)
        self.sale_order.invoice_ids.action_post()
        invoice = self.sale_order.invoice_ids[0]
        # we add the commissions on the first invoice line
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line.agent_ids = False  # Erase current agents
        self.env["account.invoice.line.agent"].create(
            {
                "object_id": invoice_line.id,
                "agent_id": self.agent.id,
                "commission_id": self.commission.id,
            }
        )
        # we test the '5% + 10% extra' commissions on the invoice too
        self.assertEqual(41.25, invoice.commission_total)

    def test_invoice_refund_commission(self):
        # we confirm the sale order and create the corresponding invoice
        self.sale_order.action_confirm()
        self.so_line.qty_delivered = self.so_line.product_uom_qty
        self._invoice_sale_order(self.sale_order)
        self.sale_order.invoice_ids.action_post()
        invoice = self.sale_order.invoice_ids[0]
        # we add the commissions on the first invoice line
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line.agent_ids = False  # Erase current agents
        self.env["account.invoice.line.agent"].create(
            {
                "object_id": invoice_line.id,
                "agent_id": self.agent.id,
                "commission_id": self.commission.id,
            }
        )
        # we test the '5% + 10% extra' commissions on the invoice too
        self.assertEqual(41.25, invoice.commission_total)
        reverse = invoice._reverse_moves(cancel=True)
        self.assertEqual(-41.25, reverse.commission_total)
