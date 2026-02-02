# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL‑3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestSaleCommissionProductCriteria(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["commission"]
        cls.company = cls.env.company
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test",
                "currency_id": cls.company.currency_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner 1",
                "property_product_pricelist": cls.pricelist.id,
                "agent_ids": [
                    (
                        6,
                        0,
                        cls.env.ref(
                            "sale_commission_product_criteria.demo_agent_rules"
                        ).ids,
                    )
                ],
            }
        )
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Test partner 2",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.settle_model = cls.env["commission.settlement"]
        cls.make_settle_model = cls.env["commission.make.settle"]
        cls.make_inv_model = cls.env["commission.make.invoice"]
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_4 = cls.env.ref("product.product_product_4")
        cls.product_5 = cls.env.ref("product.product_product_5")
        cls.product_6 = cls.env.ref("product.product_product_6")
        cls.product_1.write({"invoice_policy": "order"})
        cls.product_4.write({"invoice_policy": "order"})
        cls.product_5.write({"invoice_policy": "order"})
        cls.product_6.write({"commission_free": True})
        cls.product_template_4 = cls.env.ref(
            "product.product_product_4_product_template"
        )
        cls.product_template_4.write({"invoice_policy": "order"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.rules_commission_id = cls.env.ref(
            "sale_commission_product_criteria.demo_commission_rules"
        )
        cls.com_item_1 = cls.env.ref(
            "sale_commission_product_criteria.demo_commission_rules_item_1"
        )
        cls.com_item_2 = cls.env.ref(
            "sale_commission_product_criteria.demo_commission_rules_item_2"
        )
        cls.com_item_3 = cls.env.ref(
            "sale_commission_product_criteria.demo_commission_rules_item_3"
        )
        cls.com_item_4 = cls.env.ref(
            "sale_commission_product_criteria.demo_commission_rules_item_4"
        )

    def _create_sale_order(self, product, partner):
        return self.sale_order_model.create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": product.uom_id.id,
                            "price_unit": 1000,
                        },
                    )
                ],
            }
        )

    def _invoice_sale_order(self, sale_order, date=None):
        old_invoices = sale_order.invoice_ids
        wizard = self.advance_inv_model.with_context(
            **{
                "active_model": "sale.order",
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
            }
        ).create({"advance_payment_method": "delivered"})
        wizard.create_invoices()
        invoice = sale_order.invoice_ids - old_invoices
        return invoice

    def test_sale_commission_product_criteria_items(self):
        """Comprova noms generats per cada item de la regla."""
        # 1. "All Products"
        self.com_item_1._compute_commission_item_name_value()
        self.com_item_1.currency_id.position = "after"
        self.com_item_1._compute_commission_item_name_value()
        self.assertEqual(self.com_item_1.name, "All Products")
        self.com_item_1.write({"applied_on": "3_global"})
        # 2. Category
        self.com_item_2._compute_commission_item_name_value()
        self.assertEqual(
            self.com_item_2.name, "Category: All / Saleable / Office Furniture"
        )
        self.com_item_2.write({"applied_on": "2_product_category"})
        # 3. Product
        self.com_item_3._compute_commission_item_name_value()
        self.assertEqual(self.com_item_3.name, "Product: Customizable Desk")
        self.com_item_3.write({"applied_on": "1_product"})
        # 4. Variant
        self.com_item_4._compute_commission_item_name_value()
        self.assertEqual(
            self.com_item_4.name, "Variant: Customizable Desk (Steel, White)"
        )
        self.com_item_4.write({"applied_on": "0_product_variant"})

    def test_sale_and_invoice_commission_flow(self):
        # 3_global
        so1 = self._create_sale_order(self.product_1, self.partner)
        so1.recompute_lines_agents()
        self.assertEqual(so1.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so1.order_line.agent_ids.amount, 10)
        so1.action_confirm()
        inv1 = self._invoice_sale_order(so1)
        inv1.recompute_lines_agents()
        inv1.action_post()

        # 2_product_category
        so2 = self._create_sale_order(self.product_5, self.partner)
        so2.recompute_lines_agents()
        self.assertEqual(so2.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so2.order_line.agent_ids.amount, 20)
        so2.action_confirm()
        inv2 = self._invoice_sale_order(so2)
        inv2.recompute_lines_agents()

        # 1_product (5%)
        pp4 = self.product_template_4.product_variant_id
        so3 = self._create_sale_order(pp4, self.partner)
        so3.recompute_lines_agents()
        self.assertEqual(so3.order_line.agent_ids.amount, 50)
        so3.action_confirm()
        inv3 = self._invoice_sale_order(so3)
        inv3.recompute_lines_agents()

        # 0_product_variant (15%)
        so4 = self._create_sale_order(self.product_4, self.partner)
        so4.recompute_lines_agents()
        self.assertEqual(so4.order_line.agent_ids.amount, 150)
        so4.action_confirm()
        inv4 = self._invoice_sale_order(so4)
        inv4.recompute_lines_agents()

        # Product commission_free
        so5 = self._create_sale_order(self.product_6, self.partner)
        so5.recompute_lines_agents()  # no hi ha agents

        # Type != product
        so6 = self._create_sale_order(self.product_4, self.partner2)
        so6.recompute_lines_agents()  # segueix sense agents

        # Net amount base
        self.rules_commission_id.amount_base_type = "net_amount"
        so7 = self._create_sale_order(self.product_4, self.partner)
        so7.order_line.agent_ids._compute_amount()

        # Archive / unarchive
        self.rules_commission_id.action_archive()
        self.rules_commission_id.action_unarchive()

        # Copy
        new_rule = self.rules_commission_id.copy()
        self.assertEqual(len(new_rule.item_ids), len(self.rules_commission_id.item_ids))

        # Change commission_type validations
        self.rules_commission_id.commission_type = "fixed"
        with self.assertRaises(ValidationError):
            self.rules_commission_id.check_type_change_allowed_moves()
        with self.assertRaises(ValidationError):
            self.rules_commission_id.check_type_change_allowed_sale()

        # No rule found
        self.env.ref(
            "sale_commission_product_criteria.demo_commission_rules_item_1"
        ).unlink()
        so8 = self._create_sale_order(self.product_1, self.partner)
        so8.order_line.agent_ids._compute_amount()

        # Consistència de producte
        with self.assertRaises(ValidationError):
            self.com_item_2.categ_id = False
        with self.assertRaises(ValidationError):
            self.com_item_3.product_tmpl_id = False
        with self.assertRaises(ValidationError):
            self.com_item_4.product_id = False

        # Onchange handlers
        self.com_item_4.product_id = self.product_1
        self.com_item_4._onchange_product_id()
        self.com_item_4.with_context(
            default_applied_on="1_product"
        )._onchange_product_id()
        self.com_item_4.product_tmpl_id = self.product_template_4
        self.com_item_4._onchange_product_id()

    def test_on_create_check(self):
        f = Form(self.commission_model)
        f.name = "New commission type"
        f.save()

        so = self._create_sale_order(self.product_4, self.partner)
        self.assertEqual(
            so.order_line.agent_ids.commission_id, self.rules_commission_id
        )
        self.assertEqual(self.rules_commission_id.commission_type, "product")

        so.action_confirm()
        with self.assertRaises(ValidationError):
            self.rules_commission_id.commission_type = "fixed"
            self.rules_commission_id.onchange_commission_type()

    def _reverse_invoice(self, invoice):
        """Create a refund (out_refund) from the given invoice."""
        wizard = (
            self.env["account.move.reversal"]
            .with_context(
                active_model="account.move",
                active_ids=invoice.ids,
            )
            .create(
                {
                    "reason": "Test refund",
                    "journal_id": invoice.journal_id.id,
                    "refund_method": "refund",
                }
            )
        )
        wizard.reverse_moves()
        refund = self.env["account.move"].search(
            [("reversed_entry_id", "=", invoice.id)], limit=1
        )
        return refund

    def test_commission_sign_on_customer_refund(self):
        """The commission on the refund (out_refund) should be the negative of the original."""
        # Create a sale order with a product that has a commission rule
        so = self._create_sale_order(self.product_4, self.partner)
        so.recompute_lines_agents()
        so.action_confirm()
        inv = self._invoice_sale_order(so)
        inv.recompute_lines_agents()
        inv.action_post()

        # Commission on the original invoice line
        self.assertTrue(inv.invoice_line_ids, "The invoice has no lines.")
        orig_agent_lines = inv.invoice_line_ids[0].agent_ids
        self.assertTrue(orig_agent_lines, "The line has no commission agents.")
        orig_amount = orig_agent_lines[0].amount

        # Create and check the sign of the commission on the refund
        refund = self._reverse_invoice(inv)
        self.assertEqual(refund.move_type, "out_refund")
        refund.recompute_lines_agents()
        refund.action_post()

        self.assertTrue(refund.invoice_line_ids, "The refund has no lines.")
        refund_agent_lines = refund.invoice_line_ids[0].agent_ids
        self.assertTrue(refund_agent_lines, "The refund line has no commission agents.")
        refund_amount = refund_agent_lines[0].amount

        # The commission on the refund must be the negative of the original
        self.assertAlmostEqual(refund_amount, -orig_amount, places=2)
