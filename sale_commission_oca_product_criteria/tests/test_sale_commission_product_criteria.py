# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from datetime import date

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.sale_commission_oca.tests.test_sale_commission import (
    TestSaleCommission,
)


class TestSaleCommissionProductCriteria(TestSaleCommission):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test",
                "currency_id": cls.company.currency_id.id,
                "company_id": cls.company.id,
            }
        )
        # Create test product category
        cls.categ = cls.env["product.category"].create(
            {"name": "Test Commission Category"}
        )
        # Create product template with variants
        cls.product_template_4 = cls.env["product.template"].create(
            {
                "name": "Test Desk",
                "invoice_policy": "order",
            }
        )
        attribute = cls.env["product.attribute"].create({"name": "Color"})
        attr_val_a = cls.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": attribute.id}
        )
        attr_val_b = cls.env["product.attribute.value"].create(
            {"name": "Blue", "attribute_id": attribute.id}
        )
        cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.product_template_4.id,
                "attribute_id": attribute.id,
                "value_ids": [Command.set([attr_val_a.id, attr_val_b.id])],
            }
        )
        # Use the second variant for the variant-specific rule so that
        # product_template_4.product_variant_id (first variant) is different
        cls.product_4 = cls.product_template_4.product_variant_ids[1]
        # Create other test products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Test Generic Product", "invoice_policy": "order"}
        )
        cls.product_5 = cls.env["product.product"].create(
            {
                "name": "Test Category Product",
                "invoice_policy": "order",
                "categ_id": cls.categ.id,
            }
        )
        cls.product_6 = cls.env["product.product"].create(
            {"name": "Test Free Product", "commission_free": True}
        )
        # Create commission with product type and items
        cls.rules_commission_id = cls.env["commission"].create(
            {
                "name": "Based on Rules",
                "commission_type": "product",
            }
        )
        cls.com_item_1 = cls.env["commission.item"].create(
            {
                "commission_id": cls.rules_commission_id.id,
                "sequence": 1,
                "based_on": "sol",
                "applied_on": "3_global",
                "commission_type": "fixed",
                "fixed_amount": 10,
            }
        )
        cls.com_item_2 = cls.env["commission.item"].create(
            {
                "commission_id": cls.rules_commission_id.id,
                "sequence": 2,
                "based_on": "sol",
                "applied_on": "2_product_category",
                "commission_type": "fixed",
                "fixed_amount": 20,
                "categ_id": cls.categ.id,
            }
        )
        cls.com_item_3 = cls.env["commission.item"].create(
            {
                "commission_id": cls.rules_commission_id.id,
                "sequence": 3,
                "based_on": "sol",
                "applied_on": "1_product",
                "commission_type": "percentage",
                "percent_amount": 5,
                "product_tmpl_id": cls.product_template_4.id,
            }
        )
        cls.com_item_4 = cls.env["commission.item"].create(
            {
                "commission_id": cls.rules_commission_id.id,
                "sequence": 4,
                "based_on": "sol",
                "applied_on": "0_product_variant",
                "commission_type": "percentage",
                "percent_amount": 15,
                "product_id": cls.product_4.id,
            }
        )
        # Create agent with this commission
        cls.agent_rules = cls.env["res.partner"].create(
            {
                "name": "Agent Rules",
                "is_company": True,
                "agent": True,
                "commission_id": cls.rules_commission_id.id,
            }
        )
        # Create partners
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner 1",
                "property_product_pricelist": cls.pricelist.id,
                "commission_agent_ids": [Command.set(cls.agent_rules.ids)],
            }
        )
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Test partner 2",
                "property_product_pricelist": cls.pricelist.id,
            }
        )

    def _create_sale_order_no_co(self, product, partner, qty=1.0):
        # TestSaleCommission already has a _create_sale_order with different params
        return self.sale_order_model.create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom_id": product.uom_id.id,
                            "price_unit": 1000,
                        },
                    )
                ],
            }
        )

    def _create_invoice_no_co(
        self, product, partner, qty=1.0, invoice_date=None, move_type="out_invoice"
    ):
        # TestAccountCommission already has a _create_invoice with different params
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
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
                                        "agent_id": self.agent_rules.id,
                                        "commission_id": self.rules_commission_id.id,
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        )

    def _create_foreign_currency(self, rate):
        """Return a currency other than the company one, at the given rate."""
        currency = self.env.ref("base.EUR")
        if currency == self.company.currency_id:
            currency = self.env.ref("base.USD")
        currency.active = True
        self.env["res.currency.rate"].search(
            [("currency_id", "=", currency.id)]
        ).unlink()
        self.env["res.currency.rate"].create(
            {
                "name": date(2000, 1, 1),
                "currency_id": currency.id,
                "company_id": self.company.id,
                "rate": rate,
            }
        )
        return currency

    def _create_product_in_uom(self, uom):
        """Return a product whose reference unit of measure is the given one."""
        return self.env["product.product"].create(
            {
                "name": f"Test {uom.name} Product",
                "invoice_policy": "order",
                "uom_id": uom.id,
            }
        )

    def test_sale_commission_oca_product_criteria_items(self):
        # items names
        self.com_item_1._compute_commission_item_name_value()
        self.com_item_1.currency_id.position = "after"
        self.com_item_1._compute_commission_item_name_value()
        self.assertEqual(self.com_item_1.name, "All Products")
        self.com_item_1.write({"applied_on": "3_global"})
        self.com_item_2._compute_commission_item_name_value()
        self.assertEqual(
            self.com_item_2.name,
            f"Category: {self.categ.display_name}",
        )
        self.com_item_2.write({"applied_on": "2_product_category"})
        self.com_item_3._compute_commission_item_name_value()
        self.assertEqual(
            self.com_item_3.name,
            f"Product: {self.product_template_4.display_name}",
        )
        self.com_item_3.write({"applied_on": "1_product"})
        self.com_item_4._compute_commission_item_name_value()
        variant_name = self.product_4.with_context(
            display_default_code=False
        ).display_name
        self.assertEqual(
            self.com_item_4.name,
            f"Variant: {variant_name}",
        )
        self.com_item_4.write({"applied_on": "0_product_variant"})
        # 3_global
        so_1 = self._create_sale_order_no_co(self.product_1, self.partner)
        so_1.recompute_lines_agents()
        self.assertEqual(so_1.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so_1.order_line.agent_ids.amount, 10)
        so_1.action_confirm()
        self._invoice_sale_order(so_1)
        invoice = so_1.invoice_ids
        invoice.recompute_lines_agents()
        invoice.action_post()
        # 2_product_category
        so = self._create_sale_order_no_co(self.product_5, self.partner)
        so.recompute_lines_agents()
        self.assertEqual(so.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so.order_line.agent_ids.amount, 20)
        so.action_confirm()
        self._invoice_sale_order(so)
        invoice = so.invoice_ids
        invoice.recompute_lines_agents()
        # 1_product 5 %
        pp4 = self.product_template_4.product_variant_id
        so = self._create_sale_order_no_co(pp4, self.partner)
        so.recompute_lines_agents()
        self.assertEqual(so.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so.order_line.agent_ids.amount, 50)
        so.action_confirm()
        self._invoice_sale_order(so)
        invoice = so.invoice_ids
        invoice.recompute_lines_agents()
        # 0_product_variant 15 %
        so = self._create_sale_order_no_co(self.product_4, self.partner)
        so.recompute_lines_agents()
        self.assertEqual(so.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so.order_line.agent_ids.amount, 150)
        so.action_confirm()
        self._invoice_sale_order(so)
        invoice = so.invoice_ids
        invoice.recompute_lines_agents()
        # Commission free product
        so = self._create_sale_order_no_co(self.product_6, self.partner)
        so.recompute_lines_agents()
        self.assertFalse(so.order_line.agent_ids)
        # Type != product
        so = self._create_sale_order_no_co(self.product_4, self.partner2)
        so.recompute_lines_agents()
        # net amount
        self.rules_commission_id.amount_base_type = "net_amount"
        so = self._create_sale_order_no_co(self.product_4, self.partner)
        so.order_line.agent_ids._compute_amount()
        # archive
        self.rules_commission_id.action_archive()
        self.rules_commission_id.action_unarchive()
        # copy
        new_rule = self.rules_commission_id.copy()
        self.assertEqual(len(new_rule.item_ids), len(self.rules_commission_id.item_ids))
        # no rule found
        self.com_item_1.unlink()
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.order_line.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 0)
        # _check_product_consistency
        with self.assertRaises(ValidationError):
            self.com_item_2.categ_id = False
        with self.assertRaises(ValidationError):
            self.com_item_3.product_tmpl_id = False
        with self.assertRaises(ValidationError):
            self.com_item_4.product_id = False
        # _onchange_product_id
        self.com_item_4.product_id = self.product_1
        self.com_item_4._onchange_product_id()
        self.com_item_4.with_context(
            default_applied_on="1_product"
        )._onchange_product_id()
        self.com_item_4.product_tmpl_id = self.product_template_4
        self.com_item_4._onchange_product_id()
        self.com_item_4.product_tmpl_id = self.product_template_4
        with self.assertRaises(ValidationError):
            self.com_item_4._onchange_product_tmpl_id()

    def test_on_create_check(self):
        with Form(self.commission_model) as f:
            f.name = "New commission type"
        so = self._create_sale_order_no_co(self.product_4, self.partner)
        self.assertEqual(
            so.order_line.agent_ids.commission_id, self.rules_commission_id
        )
        self.assertEqual(self.rules_commission_id.commission_type, "product")
        so.action_confirm()
        with self.assertRaises(ValidationError):
            self.rules_commission_id.commission_type = "fixed"

    def test_type_change_blocked_by_posted_invoice(self):
        """The type of an applied commission is protected from any write, not
        only from the one of the form view."""
        invoice = self._create_invoice(self.agent_rules, self.rules_commission_id)
        invoice.action_post()
        with self.assertRaises(ValidationError):
            self.rules_commission_id.write({"commission_type": "fixed"})

    def test_type_rewritten_with_same_value_is_allowed(self):
        """Rewriting the type with the value it already holds is not a change,
        so an import or a data file reload is not rejected."""
        invoice = self._create_invoice(self.agent_rules, self.rules_commission_id)
        invoice.action_post()
        self.rules_commission_id.write({"commission_type": "product"})
        self.assertEqual(self.rules_commission_id.commission_type, "product")
        # An actual change is still blocked
        with self.assertRaises(ValidationError):
            self.rules_commission_id.write({"commission_type": "fixed"})

    def test_refund_commission_is_negative(self):
        """A refund earns the opposite of the commission of an invoice."""
        self.com_item_1.per_unit = True
        refund = self._create_invoice_no_co(
            self.product_1, self.partner, qty=3, move_type="out_refund"
        )
        agent_line = refund.invoice_line_ids.agent_ids
        self.assertEqual(agent_line.applied_commission_item_id, self.com_item_1)
        # 10 (fixed) x 3 (qty), given back on a refund
        self.assertEqual(agent_line.amount, -30)

    def test_commission_free_product_earns_nothing(self):
        """Flagging a product commission free drops the commission of the
        lines it is on, on orders as well as on invoices."""
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.recompute_lines_agents()
        invoice = self._create_invoice_no_co(self.product_1, self.partner)
        so_agent_line = so.order_line.agent_ids
        invoice_agent_line = invoice.invoice_line_ids.agent_ids
        self.assertEqual(so_agent_line.amount, 10)
        self.assertEqual(invoice_agent_line.amount, 10)
        # The lines keep their agents, as their own flag only follows
        # product_id, so the amount is what has to drop
        self.product_1.commission_free = True
        for agent_line in (so_agent_line, invoice_agent_line):
            self.assertEqual(agent_line.amount, 0)
            self.assertFalse(agent_line.applied_commission_item_id)

    def test_per_unit_fixed_amount(self):
        """Fixed amount with per_unit=True is multiplied by quantity."""
        self.com_item_1.write({"per_unit": True})
        so = self._create_sale_order_no_co(self.product_1, self.partner, qty=5)
        so.recompute_lines_agents()
        # 10 (fixed) x 5 (qty)
        self.assertEqual(so.order_line.agent_ids.amount, 50)
        # The displayed value tells a per unit fee from a flat one
        self.assertTrue(self.com_item_1.commission_value.endswith("/ unit"))

    def test_commission_value_formatting(self):
        """The rule value is formatted for the language, and carries a currency
        symbol only when the rule belongs to a company."""
        self.com_item_1.fixed_amount = 1000
        self.assertIn("1,000.00", self.com_item_1.commission_value)
        self.assertIn(self.company.currency_id.symbol, self.com_item_1.commission_value)
        # A shared rule has no currency, its amount is the one of the document
        self.com_item_1.company_id = False
        self.assertFalse(self.com_item_1.currency_id)
        self.assertEqual(self.com_item_1.commission_value, "1,000.00")

    def test_per_unit_false_preserves_behavior(self):
        """Fixed amount with per_unit=False returns flat amount."""
        so = self._create_sale_order_no_co(self.product_1, self.partner, qty=5)
        so.recompute_lines_agents()
        # 10 (fixed), quantity has no effect
        self.assertEqual(so.order_line.agent_ids.amount, 10)

    def test_fixed_amount_converted_to_order_currency(self):
        """Fixed amounts are set in company currency and converted to the
        currency of the sale order."""
        currency = self._create_foreign_currency(rate=2.0)
        self.pricelist.currency_id = currency
        self.com_item_1.per_unit = True
        so = self._create_sale_order_no_co(self.product_1, self.partner, qty=5)
        so.recompute_lines_agents()
        self.assertEqual(so.currency_id, currency)
        # 10 (fixed) x 5 (qty), converted at a rate of 2
        self.assertEqual(so.order_line.agent_ids.amount, 100)

    def test_fixed_amount_converted_to_invoice_currency(self):
        """Fixed amounts are converted to the currency of the invoice."""
        currency = self._create_foreign_currency(rate=2.0)
        invoice = self._create_invoice_no_co(self.product_1, self.partner)
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 10)
        # Changing the currency retriggers the conversion
        invoice.currency_id = currency
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 20)

    def test_percentage_amount_not_converted(self):
        """Percentages apply to a subtotal already in the document currency."""
        currency = self._create_foreign_currency(rate=2.0)
        self.pricelist.currency_id = currency
        self.com_item_1.write({"commission_type": "percentage", "percent_amount": 10})
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.recompute_lines_agents()
        line = so.order_line
        self.assertEqual(line.agent_ids.amount, line.price_subtotal * 0.10)

    def test_min_qty_threshold(self):
        """The rule with the highest applicable min_qty wins."""
        # Add a second global rule with higher min_qty and different amount
        self.env["commission.item"].create(
            {
                "commission_id": self.rules_commission_id.id,
                "sequence": 1,
                "based_on": "sol",
                "applied_on": "3_global",
                "commission_type": "fixed",
                "fixed_amount": 8,
                "min_qty": 10,
            }
        )
        # qty=5 → below threshold → original rule (fixed 10)
        so_below = self._create_sale_order_no_co(self.product_1, self.partner, qty=5)
        so_below.recompute_lines_agents()
        self.assertEqual(so_below.order_line.agent_ids.amount, 10)
        # qty=12 → above threshold → volume rule (fixed 8)
        so_above = self._create_sale_order_no_co(self.product_1, self.partner, qty=12)
        so_above.recompute_lines_agents()
        self.assertEqual(so_above.order_line.agent_ids.amount, 8)

    def test_min_qty_ignored_on_negative_quantity(self):
        """A rule without min_qty applies whatever the quantity sign is."""
        so = self._create_sale_order_no_co(self.product_1, self.partner, qty=-5)
        so.recompute_lines_agents()
        self.assertEqual(so.order_line.agent_ids.amount, 10)

    def test_quantities_in_product_uom(self):
        """min_qty and per unit amounts use the product reference UoM."""
        self.com_item_1.write({"per_unit": True, "min_qty": 10})
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.order_line.product_uom_id = self.env.ref("uom.product_uom_dozen")
        so.recompute_lines_agents()
        # 1 Dozen = 12 Units: above the 10 Units threshold, and 12 x 10
        self.assertEqual(so.order_line.agent_ids.amount, 120)

    def _create_fractional_dozen_order(self):
        """Return an order of 5 Units of a product referenced in Dozens."""
        product = self._create_product_in_uom(self.env.ref("uom.product_uom_dozen"))
        so = self._create_sale_order_no_co(product, self.partner, qty=5)
        so.order_line.product_uom_id = self.env.ref("uom.product_uom_unit")
        return so

    def test_per_unit_amount_on_fractional_uom_quantity(self):
        """The quantity in the product UoM is not rounded when converted."""
        self.com_item_1.per_unit = True
        so = self._create_fractional_dozen_order()
        so.recompute_lines_agents()
        # 5 Units is 5 / 12 Dozen, and not the 0.42 Dozen of a rounded up
        # conversion
        self.assertAlmostEqual(so.order_line.agent_ids.amount, 10 * 5 / 12)

    def test_fractional_per_unit_amount_converted_to_order_currency(self):
        """A converted fractional amount is rounded to the order currency."""
        currency = self._create_foreign_currency(rate=2.0)
        self.pricelist.currency_id = currency
        self.com_item_1.per_unit = True
        so = self._create_fractional_dozen_order()
        so.recompute_lines_agents()
        # 10 x 5 / 12 is 4.1667 in the company currency, so 8.33 at a rate of 2
        self.assertEqual(so.order_line.agent_ids.amount, 8.33)

    def test_min_qty_not_reached_by_uom_conversion(self):
        """A converted quantity does not cross a threshold it doesn't reach."""
        product = self._create_product_in_uom(self.env.ref("uom.product_uom_kgm"))
        self.env["commission.item"].create(
            {
                "commission_id": self.rules_commission_id.id,
                "based_on": "sol",
                "applied_on": "3_global",
                "commission_type": "fixed",
                "fixed_amount": 8,
                "min_qty": 1.24,
            }
        )
        so = self._create_sale_order_no_co(product, self.partner, qty=1234)
        so.order_line.product_uom_id = self.env.ref("uom.product_uom_gram")
        so.recompute_lines_agents()
        # 1234 g is 1.234 kg, below the 1.24 kg threshold of the volume rule
        self.assertEqual(so.order_line.agent_ids.amount, 10)

    def test_min_qty_on_line_without_product(self):
        """A line without product does not break the item matching."""
        self.com_item_1.min_qty = 5
        so = self._create_sale_order_no_co(self.product_1, self.partner, qty=10)
        self.env["sale.order.line"].create(
            {
                "order_id": so.id,
                "name": "A section",
                "display_type": "line_section",
            }
        )
        so.recompute_lines_agents()
        product_line, section_line = so.order_line
        self.assertEqual(product_line.agent_ids.amount, 10)
        self.assertEqual(section_line.agent_ids.amount, 0)

    def test_net_amount_base_in_product_uom(self):
        """The net amount base uses the quantity in the product UoM."""
        self.rules_commission_id.amount_base_type = "net_amount"
        self.com_item_1.write({"commission_type": "percentage", "percent_amount": 10})
        self.product_1.write({"list_price": 1000, "standard_price": 50})
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.order_line.product_uom_id = self.env.ref("uom.product_uom_dozen")
        so.recompute_lines_agents()
        line = so.order_line
        # 1 Dozen is 12 Units, so 12 times the unit cost is subtracted
        net_amount = line.price_subtotal - 12 * self.product_1.standard_price
        self.assertGreater(net_amount, 0)
        self.assertEqual(line.agent_ids.amount, net_amount * 0.10)

    def test_net_amount_base_converted_to_order_currency(self):
        """The cost subtracted from the net amount is set in the currency of
        the company and converted to the currency of the sale order."""
        currency = self._create_foreign_currency(rate=2.0)
        self.pricelist.currency_id = currency
        self.rules_commission_id.amount_base_type = "net_amount"
        self.com_item_1.write({"commission_type": "percentage", "percent_amount": 10})
        self.product_1.write({"list_price": 1000, "standard_price": 50})
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.recompute_lines_agents()
        line = so.order_line
        # The unit cost is 50 in the company currency, so 100 in the order one
        net_amount = line.price_subtotal - 100
        self.assertGreater(net_amount, 0)
        self.assertEqual(line.agent_ids.amount, net_amount * 0.10)

    def test_per_unit_and_min_qty_on_invoice(self):
        """Per unit amounts and min_qty apply to invoice lines as well."""
        self.com_item_1.write({"per_unit": True, "min_qty": 10})
        invoice = self._create_invoice_no_co(self.product_1, self.partner)
        # Below the threshold, and no other rule matches
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 0)
        # Changing the quantity retriggers the item matching: 12 x 10
        invoice.invoice_line_ids.quantity = 12
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 120)

    def test_date_validity(self):
        """Rules outside their date range are excluded."""
        # Restrict the global rule to January 2026
        self.com_item_1.write(
            {
                "date_start": date(2026, 1, 1),
                "date_end": date(2026, 1, 31),
            }
        )
        for invoice_date, amount in ((date(2026, 1, 15), 10), (date(2026, 6, 1), 0)):
            invoice = self._create_invoice_no_co(
                self.product_1, self.partner, invoice_date=invoice_date
            )
            self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, amount)

    def test_amount_recomputed_on_document_date_change(self):
        """Setting the document date retriggers the item matching."""
        self.com_item_1.write(
            {
                "date_start": date(2026, 1, 1),
                "date_end": date(2026, 1, 31),
            }
        )
        # A draft invoice has no invoice date yet, so today is used
        invoice = self._create_invoice_no_co(self.product_1, self.partner)
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 0)
        invoice.invoice_date = date(2026, 1, 15)
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 10)
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.recompute_lines_agents()
        so.date_order = "2026-01-15 12:00:00"
        self.assertEqual(so.order_line.agent_ids.amount, 10)
        so.date_order = "2026-06-01 12:00:00"
        self.assertEqual(so.order_line.agent_ids.amount, 0)

    def test_order_date_in_company_timezone(self):
        """The order date is evaluated in the company timezone, whatever the
        timezone of the user recomputing the commission is."""
        self.company.partner_id.tz = "Asia/Tokyo"
        self.env.user.tz = "America/New_York"
        self.com_item_1.date_start = date(2026, 1, 15)
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        self.assertEqual(so.company_id, self.company)
        # 2026-01-15 08:00 in Tokyo, still 2026-01-14 in UTC and in New York
        so.date_order = "2026-01-14 23:00:00"
        so.recompute_lines_agents()
        self.assertEqual(so.order_line.agent_ids.amount, 10)

    def test_date_start_after_end_raises(self):
        """Start date after end date is rejected."""
        with self.assertRaises(ValidationError):
            self.com_item_1.write(
                {
                    "date_start": date(2026, 2, 1),
                    "date_end": date(2026, 1, 1),
                }
            )

    def test_applied_item_cleared_when_item_becomes_invalid(self):
        """A previously applied item does not linger once it expires."""
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.recompute_lines_agents()
        agent_line = so.order_line.agent_ids
        self.assertEqual(agent_line.amount, 10)
        self.assertEqual(agent_line.applied_commission_item_id, self.com_item_1)
        self.com_item_1.date_end = date(2020, 1, 1)  # expires before order date
        so.order_line.product_uom_qty = 2  # retriggers the amount compute
        self.assertEqual(agent_line.amount, 0)
        self.assertFalse(agent_line.applied_commission_item_id)
        self.assertFalse(agent_line.applied_commission_id)

    def test_applied_item_cleared_on_non_product_commission(self):
        """Applied item/commission are cleared when the line's commission is
        no longer a product-criteria one (both sale and invoice lines)."""
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.recompute_lines_agents()
        invoice = self._create_invoice(self.agent_rules, self.rules_commission_id)
        # 10% of the net amount: 1000 on the order line, 5 on the invoice line
        for agent_line, net_amount in (
            (so.order_line.agent_ids, 100),
            (invoice.invoice_line_ids.agent_ids, 0.5),
        ):
            self.assertEqual(agent_line.amount, 10)
            self.assertEqual(agent_line.applied_commission_item_id, self.com_item_1)
            # Changing the commission retriggers the amount compute
            agent_line.commission_id = self.commission_net_invoice
            self.assertEqual(agent_line.amount, net_amount)
            self.assertFalse(agent_line.applied_commission_item_id)
            self.assertFalse(agent_line.applied_commission_id)

    def test_item_matching_scoped_to_document_company(self):
        """Only the rules of the company of the document apply to it, even when
        the user is allowed to see the rules of another company."""
        company = self.env["res.company"].create({"name": "Test other company"})
        self.env.user.company_ids = [Command.link(company.id)]
        self.com_item_1.company_id = company
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        self.assertEqual(so.company_id, self.company)
        so.recompute_lines_agents()
        self.assertEqual(so.order_line.agent_ids.amount, 0)
        # A rule without company is shared by all of them
        self.com_item_1.company_id = False
        so_shared = self._create_sale_order_no_co(self.product_1, self.partner)
        so_shared.recompute_lines_agents()
        self.assertEqual(so_shared.order_line.agent_ids.amount, 10)

    def test_item_multi_company_rule(self):
        """The rules of a company the user is not allowed to are hidden."""
        company = self.env["res.company"].create({"name": "Test other company"})
        user = self.env["res.users"].create(
            {
                "name": "Test commission manager",
                "login": "test_commission_manager",
                "company_id": self.company.id,
                "company_ids": [Command.set([self.company.id])],
                "group_ids": [
                    Command.link(self.env.ref("sales_team.group_sale_manager").id)
                ],
            }
        )
        self.com_item_2.company_id = company
        self.com_item_3.company_id = False
        items = self.env["commission.item"].with_user(user).search([])
        self.assertIn(self.com_item_1, items)
        self.assertNotIn(self.com_item_2, items)
        self.assertIn(self.com_item_3, items)

    def test_settlement_report_shows_applied_value(self):
        """The settlement report prints the value of the applied rule, for the
        invoicing user printing it as well: unlike the stored commission
        amount, the value is read as the user and not as superuser."""
        self.com_item_1.per_unit = True
        self._process_invoice_and_settle(self.agent_rules, self.rules_commission_id, 1)
        settlements = self.settle_model.search([("agent_id", "=", self.agent_rules.id)])
        self.assertTrue(settlements)
        user = self.env["res.users"].create(
            {
                "name": "Test invoicing user",
                "login": "test_invoicing_user",
                "company_id": self.company.id,
                "company_ids": [Command.set([self.company.id])],
                "group_ids": [
                    Command.link(self.env.ref("account.group_account_invoice").id),
                    Command.link(
                        self.env.ref("commission_oca.group_commission_manager").id
                    ),
                ],
            }
        )
        html, _report_type = (
            self.env["ir.actions.report"]
            .with_user(user)
            ._render_qweb_html("commission_oca.report_settlement", settlements.ids)
        )
        self.assertIn(self.com_item_1.commission_value, html.decode())
