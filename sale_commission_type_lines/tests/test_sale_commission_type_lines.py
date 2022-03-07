from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase
from odoo.tools import float_repr


class TestSaleCommission(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["sale.commission"]
        cls.commission_item_model = cls.env["commission.item"]
        cls.company = cls.env.ref("base.main_company")
        cls.company_usd_id = cls.env["res.company"].create(
            {"name": "USD company", "currency_id": cls.env.ref("base.USD").id}
        )
        cls.company_eur_id = cls.env["res.company"].create(
            {"name": "EUR company", "currency_id": cls.env.ref("base.EUR").id}
        )
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.write({"agent": False})
        cls.sale_order_model = cls.env["sale.order"]
        cls.product = cls.env.ref("product.product_product_5")
        cls.product.list_price = 5  # for testing specific commission section
        cls.product.write({"invoice_policy": "order"})
        cls.commission_net_paid = cls.commission_model.create(
            {
                "name": "20% fixed commission (Net amount) - Payment Based",
                "fix_qty": 20.0,
                "invoice_state": "paid",
                "amount_base_type": "net_amount",
            }
        )
        cls.commission_net_invoice = cls.commission_model.create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )
        cls.commission_section_paid = cls.commission_model.create(
            {
                "name": "Section commission - Payment Based",
                "commission_type": "section",
                "invoice_state": "paid",
                "section_ids": [
                    (0, 0, {"amount_from": 1.0, "amount_to": 100.0, "percent": 10.0})
                ],
                "amount_base_type": "net_amount",
            }
        )
        cls.commission_section_invoice = cls.commission_model.create(
            {
                "name": "Section commission - Invoice Based",
                "commission_type": "section",
                "section_ids": [
                    (
                        0,
                        0,
                        {
                            "amount_from": 15000.0,
                            "amount_to": 16000.0,
                            "percent": 20.0,
                        },
                    )
                ],
            }
        )
        cls.agent_monthly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Monthly",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
                "commission_id": cls.commission_net_invoice.id,
            }
        )
        cls.com_it_pt_fixed = cls.commission_item_model.create(
            {
                "name": "Product template fixed",
                "product_tmpl_id": cls.env.ref(
                    "product.product_product_6"
                ).product_tmpl_id.id,
                "applied_on": "1_product",
                "commission_type": "fixed",
                "fixed_amount": 100,
            }
        )
        cls.com_it_pt_precent = cls.commission_item_model.create(
            {
                "name": "Product template percent",
                "product_tmpl_id": cls.env.ref(
                    "product.product_product_6"
                ).product_tmpl_id.id,
                "applied_on": "1_product",
                "commission_type": "percentage",
                "percent_amount": 10,
            }
        )
        cls.com_it_pp_fixed = cls.commission_item_model.create(
            {
                "name": "Product product fixed",
                "product_id": cls.env.ref("product.product_product_6").id,
                "applied_on": "0_product_variant",
                "commission_type": "fixed",
                "fixed_amount": 100,
            }
        )
        cls.com_it_pp_precent = cls.commission_item_model.create(
            {
                "name": "Product product percent",
                "product_id": cls.env.ref("product.product_product_6").id,
                "applied_on": "0_product_variant",
                "commission_type": "percentage",
                "percent_amount": 10,
            }
        )
        cls.com_it_cat_fixed = cls.commission_item_model.create(
            {
                "name": "Category fixed",
                "company_id": cls.company_eur_id.id,
                "categ_id": cls.env.ref("product.product_category_5").id,
                "applied_on": "2_product_category",
                "commission_type": "fixed",
                "fixed_amount": 100,
            }
        )
        cls.com_it_cat_precent = cls.commission_item_model.create(
            {
                "name": "Category percent",
                "categ_id": cls.env.ref("product.product_category_5").id,
                "applied_on": "2_product_category",
                "commission_type": "percentage",
                "percent_amount": 10,
            }
        )
        cls.com_it_glob_fixed = cls.commission_item_model.create(
            {
                "name": "Global fixed",
                "company_id": cls.company_usd_id.id,
                "applied_on": "3_global",
                "commission_type": "fixed",
                "fixed_amount": 100,
            }
        )
        cls.com_it_glob_precent = cls.commission_item_model.create(
            {
                "name": "Global percent",
                "applied_on": "3_global",
                "commission_type": "percentage",
                "percent_amount": 10,
            }
        )
        cls.commission_prod_cat_var_fixed = cls.commission_model.create(
            {
                "name": "Multiline commission fixed",
                "commission_type": "cat_prod_var",
                "amount_base_type": "net_amount",
                "item_ids": [
                    (
                        6,
                        0,
                        [
                            cls.com_it_cat_fixed.id,
                            cls.com_it_pp_fixed.id,
                            cls.com_it_pt_fixed.id,
                        ],
                    )
                ],
            }
        )
        cls.commission_prod_cat_var_percent = cls.commission_model.create(
            {
                "name": "Multiline commission percent",
                "commission_type": "cat_prod_var",
                "item_ids": [
                    (
                        6,
                        0,
                        [
                            cls.com_it_cat_precent.id,
                            cls.com_it_pp_precent.id,
                            cls.com_it_pt_precent.id,
                        ],
                    )
                ],
            }
        )
        cls.agent_cpv_fixed = cls.res_partner_model.create(
            {
                "name": "CPV fixed",
                "agent": True,
                "lang": "en_US",
                "commission_id": cls.commission_prod_cat_var_fixed.id,
            }
        )
        cls.agent_cpv_percent = cls.res_partner_model.create(
            {
                "name": "CPV percent",
                "agent": True,
                "lang": "en_US",
                "commission_id": cls.commission_prod_cat_var_percent.id,
            }
        )

    def _create_sale_order(self, agent, commission):
        return self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": self.product.lst_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": agent.id,
                                        "commission_id": commission.id,
                                    },
                                )
                            ],
                        },
                    )
                ],
            }
        )

    def test_commission_items_created(self):
        # Check if computed name is correct
        self.assertEqual(
            self.com_it_pt_fixed.name,
            "Product: " + self.com_it_pt_fixed.product_tmpl_id.display_name,
        )
        self.assertEqual(
            self.com_it_pp_fixed.name,
            "Variant: " + self.com_it_pp_fixed.product_id.name,
        )
        self.assertEqual(
            self.com_it_cat_fixed.name,
            "Category: " + self.com_it_cat_fixed.categ_id.display_name,
        )
        self.assertEqual(self.com_it_glob_fixed.name, "All Products")
        # Check if computed commission_value is correct
        # ... USD
        amount = float_repr(
            self.com_it_glob_fixed.fixed_amount,
            self.env["decimal.precision"].precision_get("Product Price"),
        )
        usd_like = self.com_it_glob_fixed.currency_id.symbol + " " + str(amount)
        self.assertEqual(self.com_it_glob_fixed.commission_value, usd_like)
        # ... EUR
        amount = float_repr(
            self.com_it_cat_fixed.fixed_amount,
            self.env["decimal.precision"].precision_get("Product Price"),
        )
        eur_like = str(amount) + " " + self.com_it_cat_fixed.currency_id.symbol
        self.assertEqual(self.com_it_cat_fixed.commission_value, eur_like)
        # ... Percent
        self.assertEqual(self.com_it_glob_precent.commission_value, "10.0 %")
        # Check _check_product_consistency()
        with self.assertRaises(ValidationError):
            self.commission_item_model.create(
                {
                    "name": "Wrong Commission Item",
                    "categ_id": False,
                    "applied_on": "2_product_category",
                    "commission_type": "percentage",
                    "percent_amount": 10,
                }
            )
        with self.assertRaises(ValidationError):
            self.commission_item_model.create(
                {
                    "name": "Wrong Commission Item",
                    "product_tmpl_id": False,
                    "applied_on": "1_product",
                    "commission_type": "percentage",
                    "percent_amount": 10,
                }
            )
        with self.assertRaises(ValidationError):
            self.commission_item_model.create(
                {
                    "name": "Wrong Commission Item",
                    "product_id": False,
                    "applied_on": "0_product_variant",
                    "commission_type": "percentage",
                    "percent_amount": 10,
                }
            )
        # _onchange_compute_price()
        self.com_it_glob_fixed.percent_amount = 50
        self.com_it_glob_fixed._onchange_compute_price()
        self.assertEqual(self.com_it_glob_fixed.percent_amount, 0.0)
        self.com_it_glob_precent.fixed_amount = 5000
        self.com_it_glob_precent._onchange_compute_price()
        self.assertEqual(self.com_it_glob_precent.fixed_amount, 0.0)
        # _onchange_product_id()
        self.com_it_pp_fixed.with_context(
            {"default_applied_on": "1_product"}
        )._onchange_product_id()
        self.assertEqual(self.com_it_pp_fixed.applied_on, "0_product_variant")
        # _onchange_product_tmpl_id
        self.com_it_pt_fixed.product_id = self.env.ref("product.product_product_4")
        self.com_it_pt_fixed._onchange_product_tmpl_id()
        self.assertFalse(self.com_it_pt_fixed.product_id)
        # write
        cat_id = self.env.ref("product.product_category_6").id
        product_id = self.env.ref("product.product_product_3").id
        product_tmpl_id = self.env.ref("product.product_product_3").product_tmpl_id.id
        vals = {
            "applied_on": "3_global",
            "categ_id": cat_id,
            "product_tmpl_id": product_id,
            "product_id": product_tmpl_id,
        }
        self.com_it_glob_fixed.write(vals.copy())
        self.assertFalse(
            self.com_it_glob_fixed.categ_id.id
            or self.com_it_glob_fixed.product_tmpl_id.id
            or self.com_it_glob_fixed.product_id.id
        )

        vals["applied_on"] = "2_product_category"
        self.com_it_cat_fixed.write(vals.copy())
        self.assertFalse(
            self.com_it_cat_fixed.product_tmpl_id.id
            or self.com_it_cat_fixed.product_id.id
        )

        vals["applied_on"] = "1_product"
        self.com_it_pt_fixed.write(vals.copy())
        self.assertFalse(
            self.com_it_pt_fixed.categ_id.id or self.com_it_pt_fixed.product_id.id
        )

        vals["applied_on"] = "0_product_variant"
        self.com_it_pt_fixed.write(vals.copy())
        self.assertFalse(self.com_it_pt_fixed.categ_id.id)

    def test_multiline_commission(self):
        sale_order_fixed = self._create_sale_order(
            self.agent_cpv_fixed, self.commission_prod_cat_var_fixed
        )
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 1
        sale_order_fixed.action_confirm()

        sale_order_percent = self._create_sale_order(
            self.agent_cpv_percent, self.commission_prod_cat_var_percent
        )
        sale_order_percent.order_line[0].product_id = self.env.ref(
            "product.product_product_6"
        ).id
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.env.ref("product.product_product_2")
            line_form.product_uom_qty = 1
        sale_order_percent.action_confirm()

        sale_order_percent = self._create_sale_order(
            self.agent_cpv_percent, self.commission_prod_cat_var_percent
        )
        prod = self.env.ref("product.product_product_2")
        prod.commission_free = True
        sale_order_percent.order_line[0].product_id = prod.id
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.env.ref("product.product_product_2")
            line_form.product_uom_qty = 1
        sale_order_percent.action_confirm()

        sale_order_percent = self._create_sale_order(
            self.agent_monthly, self.commission_net_paid
        )
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.env.ref("product.product_product_2")
            line_form.product_uom_qty = 1
        sale_order_percent.action_confirm()

        sale_order_percent = self._create_sale_order(
            self.agent_monthly, self.commission_section_paid
        )
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.env.ref("product.product_product_2")
            line_form.product_uom_qty = 1
        sale_order_percent.action_confirm()

        sale_order_paid = self._create_sale_order(
            self.agent_monthly, self.commission_net_paid
        )
        prod = self.env.ref("product.product_product_2")
        prod.commission_free = True
        sale_order_paid.order_line[0].product_id = prod.id
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.env.ref("product.product_product_2")
            line_form.product_uom_qty = 1
        sale_order_paid.action_confirm()
