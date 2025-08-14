# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html


from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestSaleCommission(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["commission"]
        cls.company = cls.env.ref("base.main_company")
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.partner2 = cls.env.ref("base.res_partner_10")
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
            [("type", "=", "purchase")], limit=1
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
        ).create(
            {
                "advance_payment_method": "delivered",
            }
        )
        wizard.create_invoices()
        invoice = sale_order.invoice_ids - old_invoices
        return invoice

    def test_sale_commission_product_criteria_items(self):
        # items names
        self.com_item_1._compute_commission_item_name_value()
        self.com_item_1.currency_id.position = "after"
        self.com_item_1._compute_commission_item_name_value()
        self.assertEqual(self.com_item_1.name, "All Products")
        self.com_item_1.write({"applied_on": "3_global"})
        self.com_item_2._compute_commission_item_name_value()
        self.assertEqual(
            self.com_item_2.name, "Category: All / Saleable / Office Furniture"
        )
        self.com_item_2.write({"applied_on": "2_product_category"})
        self.com_item_3._compute_commission_item_name_value()
        self.assertEqual(self.com_item_3.name, "Product: Customizable Desk")
        self.com_item_3.write({"applied_on": "1_product"})
        self.com_item_4._compute_commission_item_name_value()
        self.assertEqual(
            self.com_item_4.name, "Variant: Customizable Desk (Steel, White)"
        )
        self.com_item_4.write({"applied_on": "0_product_variant"})

        # 3_global
        so_1 = self._create_sale_order(self.product_1, self.partner)
        so_1.recompute_lines_agents()
        self.assertEqual(so_1.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so_1.order_line.agent_ids.amount, 10)
        so_1.action_confirm()
        invoice = self._invoice_sale_order(so_1)
        invoice.recompute_lines_agents()
        invoice.action_post()

        # 2_product_category
        so = self._create_sale_order(self.product_5, self.partner)
        so.recompute_lines_agents()
        self.assertEqual(so.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so.order_line.agent_ids.amount, 20)
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()

        # 1_product 5 %
        pp4 = self.product_template_4.product_variant_id
        so = self._create_sale_order(pp4, self.partner)
        so.recompute_lines_agents()
        self.assertEqual(so.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so.order_line.agent_ids.amount, 50)
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()

        # 0_product_variant 15 %
        so = self._create_sale_order(self.product_4, self.partner)
        so.recompute_lines_agents()
        self.assertEqual(so.partner_agent_ids.name, "Agent Rules")
        self.assertEqual(so.order_line.agent_ids.amount, 150)
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()

        # Commission free product
        so = self._create_sale_order(self.product_6, self.partner)
        so.recompute_lines_agents()

        # Type != product
        so = self._create_sale_order(self.product_4, self.partner2)
        so.recompute_lines_agents()

        # net amount
        self.rules_commission_id.amount_base_type = "net_amount"
        so = self._create_sale_order(self.product_4, self.partner)
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
        self.env.ref(
            "sale_commission_product_criteria.demo_commission_rules_item_1"
        ).unlink()
        so = self._create_sale_order(self.product_1, self.partner)
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
