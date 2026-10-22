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
        # Also once invoiced, while rewriting the same value as an import does
        # is not a change
        invoice = self._create_invoice(self.agent_rules, self.rules_commission_id)
        invoice.action_post()
        self.rules_commission_id.write({"commission_type": "product"})
        with self.assertRaises(ValidationError):
            self.rules_commission_id.write({"commission_type": "fixed"})

    def test_item_conditions(self):
        """Per unit amounts, minimum quantities and validity dates of the items,
        matched again when the document changes."""
        volume_item = self.env["commission.item"].create(
            {
                "commission_id": self.rules_commission_id.id,
                "based_on": "sol",
                "applied_on": "3_global",
                "commission_type": "fixed",
                "fixed_amount": 8,
                "per_unit": True,
                "min_qty": 10,
            }
        )
        self.com_item_1.per_unit = True
        self.assertTrue(self.com_item_1.commission_value.endswith("/ unit"))
        so = self._create_sale_order_no_co(self.product_1, self.partner, qty=5)
        so.recompute_lines_agents()
        line = so.order_line
        self.assertEqual(line.agent_ids.amount, 50)
        line.product_uom_qty = 12
        self.assertEqual(line.agent_ids.amount, 96)
        with self.assertRaises(ValidationError):
            volume_item.write(
                {"date_start": date(2026, 2, 1), "date_end": date(2026, 1, 1)}
            )
        volume_item.write(
            {"date_start": date(2026, 1, 15), "date_end": date(2026, 1, 31)}
        )
        # The order date is evaluated in the company timezone: 2026-01-15 08:00
        # in Tokyo is still 2026-01-14 in UTC and in New York
        self.company.partner_id.tz = "Asia/Tokyo"
        self.env.user.tz = "America/New_York"
        so.date_order = "2026-01-14 23:00:00"
        self.assertEqual(line.agent_ids.amount, 96)
        so.date_order = "2026-06-01 12:00:00"
        self.assertEqual(line.agent_ids.amount, 120)
        invoice = self._create_invoice_no_co(
            self.product_1, self.partner, qty=11, invoice_date=date(2026, 6, 1)
        )
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 110)
        invoice.invoice_date = date(2026, 1, 20)
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 88)
        # Fixed amounts are converted from the company currency
        invoice.currency_id = self._create_foreign_currency(rate=2.0)
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 176)
        # Only the items of the company of the document apply to it
        company = self.env["res.company"].create({"name": "Test other company"})
        self.env.user.company_ids = [Command.link(company.id)]
        volume_item.company_id = company
        invoice.invoice_line_ids.quantity = 12
        self.assertEqual(invoice.invoice_line_ids.agent_ids.amount, 240)
        refund = self._create_invoice_no_co(
            self.product_1, self.partner, qty=3, move_type="out_refund"
        )
        self.assertEqual(refund.invoice_line_ids.agent_ids.amount, -30)
        # The applied item is cleared once the commission is not a product
        # criteria one, or the product is flagged commission free
        agent_line = invoice.invoice_line_ids.agent_ids
        agent_line.commission_id = self.commission_net_invoice
        self.assertFalse(agent_line.applied_commission_item_id)
        self.assertFalse(agent_line.applied_commission_id)
        self.assertEqual(line.agent_ids.applied_commission_item_id, self.com_item_1)
        self.product_1.commission_free = True
        self.assertEqual(line.agent_ids.amount, 0)
        self.assertFalse(line.agent_ids.applied_commission_item_id)

    def _reverse_invoice(self, invoice, reversal_date):
        """Return the credit note of the reversal wizard for an invoice."""
        self.env["account.move.reversal"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create(
            {"date": reversal_date, "journal_id": invoice.journal_id.id}
        ).refund_moves()
        return invoice.reversal_move_ids

    def test_refund_keeps_invoice_item(self):
        """A credit note gives back the commission at the item the refunded
        line earned, not at the one matching its own date and quantity."""
        self.com_item_1.per_unit = True
        volume_item = self.env["commission.item"].create(
            {
                "commission_id": self.rules_commission_id.id,
                "based_on": "sol",
                "applied_on": "3_global",
                "commission_type": "fixed",
                "fixed_amount": 8,
                "per_unit": True,
                "min_qty": 10,
                "date_end": date(2026, 1, 31),
            }
        )
        invoice = self._create_invoice_no_co(
            self.product_1, self.partner, qty=3, invoice_date=date(2026, 1, 15)
        )
        invoice.invoice_line_ids = [
            Command.create(
                {
                    "product_id": self.product_1.id,
                    "quantity": 12,
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
        ]
        invoice.action_post()
        self.assertEqual(invoice.invoice_line_ids.agent_ids.mapped("amount"), [30, 96])
        # Dated after the volume item expired, below its minimum quantity, and
        # without the other line of the same product
        refund = self._reverse_invoice(invoice, date(2026, 6, 1))
        refund.invoice_line_ids = [Command.unlink(refund.invoice_line_ids[0].id)]
        refund.invoice_line_ids.quantity = 3
        agent_line = refund.invoice_line_ids.agent_ids
        self.assertEqual(agent_line.applied_commission_item_id, volume_item)
        self.assertEqual(agent_line.amount, -24)
        # A line added to the credit note has no item to reuse
        refund.invoice_line_ids = [
            Command.create(
                {"product_id": self.product_1.id, "quantity": 2, "price_unit": 1000}
            )
        ]
        added_agent_line = refund.invoice_line_ids.agent_ids - agent_line
        self.assertEqual(added_agent_line.applied_commission_item_id, self.com_item_1)
        self.assertEqual(added_agent_line.amount, -20)
