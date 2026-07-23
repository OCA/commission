# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

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

    def _create_sale_order_no_co(self, product, partner):
        # TestSaleCommission already has a _create_sale_order with different params
        return self.sale_order_model.create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
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
        # change commission_type
        self.rules_commission_id.commission_type = "fixed"
        with self.assertRaises(ValidationError):
            self.rules_commission_id.check_type_change_allowed_moves()
        with self.assertRaises(ValidationError):
            self.rules_commission_id.check_type_change_allowed_sale()
        # no rule found
        self.com_item_1.unlink()
        so = self._create_sale_order_no_co(self.product_1, self.partner)
        so.order_line.agent_ids._compute_amount()
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
            self.rules_commission_id.onchange_commission_type()
