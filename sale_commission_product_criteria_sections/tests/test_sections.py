# Copyright 2025 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleCommissionProductCriteriaSections(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["commission"]
        cls.item_model = cls.env["commission.item"]
        cls.product_model = cls.env["product.product"]

        # Sections are closed intervals, the first matching one is applied.
        cls.section_commission = cls._create_commission("Product criteria by sections")
        cls.section_item = cls.item_model.create(
            {
                "commission_id": cls.section_commission.id,
                "based_on": "sol",
                "applied_on": "3_global",
                "commission_type": "section",
                "section_ids": [
                    (0, 0, {"amount_from": 0.0, "amount_to": 100.0, "percent": 5.0}),
                    (
                        0,
                        0,
                        {
                            "amount_from": 100.01,
                            "amount_to": 500.0,
                            "percent": 8.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "amount_from": 500.01,
                            "amount_to": 1000.0,
                            "percent": 10.0,
                        },
                    ),
                ],
            }
        )
        # Rules more specific than the global one above take precedence,
        # so the other commission types can be checked with their product.
        cls.product_fixed = cls._create_product("Fixed amount product")
        cls.fixed_item = cls.item_model.create(
            {
                "commission_id": cls._create_commission(
                    "Product criteria by fixed amount"
                ).id,
                "based_on": "sol",
                "applied_on": "1_product",
                "commission_type": "fixed",
                "fixed_amount": 42.0,
                "product_tmpl_id": cls.product_fixed.product_tmpl_id.id,
            }
        )
        cls.product_percentage = cls._create_product("Percentage product")
        cls.percentage_item = cls.item_model.create(
            {
                "commission_id": cls._create_commission(
                    "Product criteria by percentage"
                ).id,
                "based_on": "sol",
                "applied_on": "0_product_variant",
                "commission_type": "percentage",
                "percent_amount": 10.0,
                "product_id": cls.product_percentage.id,
            }
        )
        cls.empty_commission = cls._create_commission("Without commission items")

        cls.product = cls._create_product("Generic product", standard_price=100.0)
        cls.partner = cls._create_partner(
            "Customer by sections", cls.section_commission
        )
        cls.partner_fixed = cls._create_partner(
            "Customer by fixed amount", cls.fixed_item.commission_id
        )
        cls.partner_percentage = cls._create_partner(
            "Customer by percentage", cls.percentage_item.commission_id
        )
        cls.partner_without_items = cls._create_partner(
            "Customer without commission items", cls.empty_commission
        )
        cls.partner_without_agent = cls.env["res.partner"].create(
            {"name": "Customer without agent"}
        )

    @classmethod
    def _create_commission(cls, name):
        return cls.commission_model.create({"name": name, "commission_type": "product"})

    @classmethod
    def _create_product(cls, name, standard_price=0.0):
        return cls.product_model.create(
            {"name": name, "standard_price": standard_price, "list_price": 0.0}
        )

    @classmethod
    def _create_partner(cls, name, commission):
        agent = cls.env["res.partner"].create(
            {
                "name": "Agent of %s" % name,
                "agent": True,
                "commission_id": commission.id,
            }
        )
        return cls.env["res.partner"].create(
            {"name": name, "agent_ids": [(6, 0, agent.ids)]}
        )

    def _create_sale_order(self, partner, price_unit, product=None, quantity=1.0):
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": (product or self.product).id,
                            "product_uom_qty": quantity,
                            "price_unit": price_unit,
                        },
                    )
                ],
            }
        )
        order.recompute_lines_agents()
        return order

    def _invoice_sale_order(self, sale_order):
        old_invoices = sale_order.invoice_ids
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                active_model="sale.order",
                active_ids=sale_order.ids,
                active_id=sale_order.id,
            )
            .create({"advance_payment_method": "delivered"})
        )
        wizard.create_invoices()
        return sale_order.invoice_ids - old_invoices

    def _get_commission_amount(self, partner, price_unit, **kwargs):
        order = self._create_sale_order(partner, price_unit, **kwargs)
        return order.order_line.agent_ids.amount

    def test_section_commission_value(self):
        self.assertEqual(self.section_item.commission_type, "section")
        self.assertEqual(self.section_item.commission_value, "By sections")
        self.assertEqual(self.section_item.name, "All Products")

    def test_section_commission_amount(self):
        # (base amount, expected commission amount)
        for base_amount, expected_amount in [
            (50.0, 2.5),
            (100.0, 5.0),  # upper limit of the first section
            (100.01, 8.0008),  # lower limit of the second section
            (200.0, 16.0),
            (500.0, 40.0),  # upper limit of the second section
            (500.01, 50.001),  # lower limit of the third section
            (1000.0, 100.0),  # upper limit of the third section
            (1500.0, 0.0),  # out of any section
        ]:
            amount = self._get_commission_amount(self.partner, base_amount)
            self.assertAlmostEqual(
                amount, expected_amount, places=2, msg="Base amount %s" % base_amount
            )

    def test_section_commission_amount_with_quantity(self):
        order = self._create_sale_order(self.partner, 100.0, quantity=3.0)
        # 3 * 100 = 300, which is inside the second section: 300 * 8%
        self.assertAlmostEqual(order.order_line.agent_ids.amount, 24.0, places=2)

    def test_calculate_section_amount(self):
        self.assertAlmostEqual(self.section_item._calculate_section_amount(200.0), 16.0)
        # Amounts out of any section have no commission at all
        self.assertEqual(self.section_item._calculate_section_amount(1500.0), 0.0)
        item_without_sections = self.item_model.create(
            {
                "commission_id": self.empty_commission.id,
                "based_on": "sol",
                "applied_on": "3_global",
                "commission_type": "section",
            }
        )
        self.assertEqual(item_without_sections._calculate_section_amount(100.0), 0.0)

    def test_section_commission_amount_from_net_amount(self):
        self.section_commission.amount_base_type = "net_amount"
        # 600 - 100 (cost) = 500, which is inside the second section: 500 * 8%
        amount = self._get_commission_amount(self.partner, 600.0)
        self.assertAlmostEqual(amount, 40.0, places=2)

    def test_section_commission_amount_below_cost(self):
        self.section_commission.amount_base_type = "net_amount"
        # The base is zeroed (50 - 100 < 0), so the commission is zero
        amount = self._get_commission_amount(self.partner, 50.0)
        self.assertAlmostEqual(amount, 0.0, places=2)

    def test_other_commission_types_are_kept(self):
        amount = self._get_commission_amount(
            self.partner_fixed, 200.0, product=self.product_fixed
        )
        self.assertAlmostEqual(amount, 42.0, places=2)
        amount = self._get_commission_amount(
            self.partner_percentage, 200.0, product=self.product_percentage
        )
        self.assertAlmostEqual(amount, 20.0, places=2)

    def test_commission_without_items(self):
        amount = self._get_commission_amount(self.partner_without_items, 200.0)
        self.assertAlmostEqual(amount, 0.0, places=2)

    def test_order_line_without_agents(self):
        order = self._create_sale_order(self.partner_without_agent, 200.0)
        self.assertFalse(order.order_line.agent_ids)
        self.assertFalse(order.order_line.agent_ids.amount)

    def test_section_commission_amount_on_invoice(self):
        order = self._create_sale_order(self.partner, 200.0)
        order.action_confirm()
        invoice = self._invoice_sale_order(order)
        invoice.recompute_lines_agents()
        # The commission of the order line is computed again on the invoice
        # line, which is inside the second section: 200 * 8%
        self.assertAlmostEqual(
            invoice.invoice_line_ids.agent_ids.amount, 16.0, places=2
        )

    def test_sections_are_copied_with_the_item(self):
        new_item = self.section_item.copy()
        self.assertNotEqual(new_item.id, self.section_item.id)
        self.assertEqual(len(new_item.section_ids), len(self.section_item.section_ids))
        self.assertAlmostEqual(
            new_item._calculate_section_amount(200.0), 16.0, places=2
        )

    def test_sections_are_removed_with_the_item(self):
        section_ids = self.section_item.section_ids.ids
        self.section_item.unlink()
        sections = self.env["commission.section"].browse(section_ids).exists()
        self.assertFalse(sections)
