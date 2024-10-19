from odoo.tests.common import TransactionCase


class TestSaleCommissionDeliveryPartner(TransactionCase):
    def setUp(self):
        super(TestSaleCommissionDeliveryPartner, self).setUp()

        self.user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "test_user@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("sale.group_delivery_invoice_address").id,
                            self.env.ref("sales_team.group_sale_manager").id,
                        ],
                    )
                ],
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@partner.com",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "standard_price": 50.0,
                "invoice_policy": "order",
                "type": "consu",
            }
        )

    def test_create_sale_order(self):
        sale_order = (
            self.env["sale.order"]
            .with_user(self.user.id)
            .create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "product_uom_qty": 5,
                                "price_unit": self.product.list_price,
                            },
                        )
                    ],
                }
            )
        )

        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")

        context = {"active_model": "sale.order", "active_ids": sale_order.ids}
        invoice_so_wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(context)
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        invoice_so_wizard.create_invoices()

        invoice_so = self.env["account.move"].search(
            [("invoice_origin", "=", sale_order.name)], limit=1
        )

        self.assertEqual(sale_order.partner_shipping_id, invoice_so.partner_shipping_id)

        new_shipping_partner = self.env["res.partner"].create(
            {
                "name": "New Shipping Partner",
                "email": "new_shipping@partner.com",
            }
        )
        sale_order.partner_shipping_id = new_shipping_partner.id

        for line in sale_order.order_line:
            for agent in line.agent_ids:
                self.assertEqual(agent.partner_id, new_shipping_partner)

        invoice_so.refresh()

        invoice_so.partner_shipping_id = new_shipping_partner.id

        for line in invoice_so.line_ids:
            for agent in line.agent_ids:
                self.assertEqual(agent.partner_id, new_shipping_partner)

        self.assertEqual(sale_order.partner_shipping_id, invoice_so.partner_shipping_id)
