#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestTripleDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Allow to see discounts on sale order lines
        cls.env.user.groups_id += cls.env.ref("product.group_discount_per_so_line")

        cls.commission = cls.env["commission"].create(
            {
                "name": "Test triple discount commission",
                "commission_type": "product",
                "item_ids": [
                    Command.create(
                        {
                            "based_on": "discount",
                            "used_discount": "computed",
                            "discount_from": 20,
                            "discount_to": 100,
                            "fixed_amount": 5,
                        }
                    ),
                ],
            }
        )

        agent_form = Form(cls.env["res.partner"])
        agent_form.name = "Agent"
        agent_form.agent = True
        agent_form.commission_id = cls.commission
        cls.agent = agent_form.save()

        customer_form = Form(cls.env["res.partner"])
        customer_form.name = "Customer"
        customer_form.agent_ids.clear()
        customer_form.agent_ids.add(cls.agent)
        cls.customer = customer_form.save()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
            }
        )

    def test_apply_commission_computed_discount(self):
        """
        Create a commission that only applies if computed discount is above 20%,
        create a sale order having total discount above 20%,
        check that the commission is applied.
        """
        product = self.product
        commission_amount = 5
        commission = self.commission
        commission_item = commission.item_ids
        agent = self.agent
        customer = self.customer
        # pre-condition
        self.assertEqual(commission.commission_type, "product")
        self.assertRecordValues(
            commission_item,
            [
                {
                    "based_on": "discount",
                    "used_discount": "computed",
                    "discount_from": 20,
                    "discount_to": 100,
                    "fixed_amount": commission_amount,
                },
            ],
        )
        self.assertEqual(agent.commission_id, commission)
        self.assertEqual(customer.agent_ids, agent)

        # Act
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = customer
        with order_form.order_line.new() as line:
            line.product_id = product
            line.discount = 10
            line.discount2 = 10
            line.discount3 = 10
        order = order_form.save()

        # Assert
        self.assertRecordValues(
            order.order_line.agent_ids,
            [
                {
                    "agent_id": agent.id,
                    "commission_id": commission.id,
                    "amount": commission_amount,
                },
            ],
        )
