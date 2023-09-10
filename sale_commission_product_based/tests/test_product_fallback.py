#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestProductFixed (SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        category_model = cls.env['product.category']
        parent_category_form = Form(category_model)
        parent_category_form.name = "Test parent category product_fallback"
        parent_category = parent_category_form.save()

        child_category_form = Form(category_model)
        child_category_form.name = "Test child category product_fallback"
        child_category_form.parent_id = parent_category
        child_category = child_category_form.save()

        product_form = Form(cls.env['product.product'])
        product_form.name = "Test product product_fallback"
        product_form.lst_price = 100
        product_form.categ_id = child_category
        cls.product_1 = product_form.save()
        cls.product_2 = cls.product_1.copy()
        cls.product_3 = cls.product_1.copy()
        cls.product_3.categ_id = parent_category

        commission_form = Form(cls.env['sale.commission'])
        commission_form.name = "Test commission product_fallback"
        commission_form.commission_type = 'product_fallback'
        commission_form.product_fallback_amount = 1
        # Rule to match `product_1`
        with commission_form.product_rule_ids.new() as rule:
            rule.product_id = cls.product_1
            rule.amount = 2
            rule.sequence = 1
        # Rule to match `product_1` and `product_2`
        with commission_form.product_rule_ids.new() as rule:
            rule.product_category_id = child_category
            rule.amount = 3
            rule.sequence = 2
        cls.commission = commission_form.save()

        agent_form = Form(cls.env['res.partner'])
        agent_form.name = "Test agent product_fallback"
        agent_form.agent = True
        agent_form.commission = cls.commission
        cls.agent = agent_form.save()

        customer_form = Form(cls.env['res.partner'])
        customer_form.name = "Test customer product_fallback"
        customer_form.customer = True
        customer_form.agents.clear()
        customer_form.agents.add(cls.agent)
        cls.customer = customer_form.save()

    def _create_order(self, products):
        order_form = Form(self.env['sale.order'])
        order_form.partner_id = self.customer
        for product in products:
            with order_form.order_line.new() as order_line:
                order_line.product_id = product
        order = order_form.save()
        return order

    def test_commission_amount(self):
        """
        Check that commission by product and by category are computed correctly.
        """
        rules = self.commission.product_rule_ids
        category_rule = rules.filtered('product_category_id')
        product_rule = rules.filtered('product_id')
        # pre-condition: One product will be matched exactly,
        # the other by category.
        # Product rule comes before category rule
        self.assertTrue(
            self.product_1 == product_rule.product_id,
        )
        self.assertTrue(
            self.product_2.categ_id == category_rule.product_category_id,
        )
        self.assertLess(product_rule.sequence, category_rule.sequence)
        self.assertEqual(self.commission.product_fallback_amount, 1)
        self.assertEqual(product_rule.amount, 2)
        self.assertEqual(category_rule.amount, 3)

        # Act
        order = self._create_order(
            self.product_1
            | self.product_2
            | self.product_3,
        )

        # Assert:
        # One product will not be matched:
        # the commission percentage will be 1 (fallback).
        # One product will be matched exactly:
        # the commission percentage will be 2 (product rule).
        # One product will be matched by category:
        # the commission percentage will be 3 (category rule).
        self.assertEqual(
            order.commission_total,
            100 * 1 / 100
            + 100 * 2 / 100
            + 100 * 3 / 100,
        )

    def test_commission_amount_sequence_match(self):
        """
        Check that sequence of the rules matters.
        """
        # Arrange: set the sequence of the rules
        # so that the category rule comes before the product rule
        rules = self.commission.product_rule_ids
        category_rule = rules.filtered('product_category_id')
        product_rule = rules.filtered('product_id')
        product_rule.sequence = category_rule.sequence + 1
        # pre-condition: Both products have the same category
        # that is also the rule's category
        self.assertTrue(
            self.product_1.categ_id
            == self.product_2.categ_id
            == category_rule.product_category_id,
        )
        self.assertEqual(self.commission.product_fallback_amount, 1)
        self.assertEqual(product_rule.amount, 2)
        self.assertEqual(category_rule.amount, 3)

        # Act
        order = self._create_order(
            self.product_1
            | self.product_2
            | self.product_3,
        )

        # Assert: Two products will be matched by category:
        # the commission percentage for each one will be 3 (category rule).
        # One product will not be matched:
        # the commission percentage will be 1 (fallback).
        self.assertEqual(
            order.commission_total,
            2 * (100 * 3 / 100)
            + 100 * 1 / 100,
        )
