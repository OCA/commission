# Copyright 2023 - ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo.exceptions
from odoo.tests.common import SavepointCase


class TestSaleCommissionDomain(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCommissionDomain, cls).setUpClass()
        cls.commission_model = cls.env["sale.commission"]
        cls.company = cls.env.ref("base.main_company")
        cls.res_partner_model = cls.env["res.partner"]
        cls.azure = cls.env.ref("base.res_partner_12")  # Azure
        cls.deco = cls.env.ref("base.res_partner_2")  # Deco
        cls.partner2 = cls.env.ref("base.res_partner_10")  # The Jackson Group
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.settle_model = cls.env["sale.commission.settlement"]
        cls.make_settle_model = cls.env["sale.commission.make.settle"]
        cls.make_inv_model = cls.env["sale.commission.make.invoice"]
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_4 = cls.env.ref("product.product_product_4")
        cls.product_5 = cls.env.ref("product.product_product_5")
        cls.product_6 = cls.env.ref("product.product_product_6")
        # Acoustic Bloc Screens
        cls.product_product_25 = cls.env.ref("product.product_product_25")
        cls.product_1.write({"invoice_policy": "order"})
        cls.product_4.write({"invoice_policy": "order"})
        cls.product_5.write({"invoice_policy": "order"})
        cls.product_product_25.write({"invoice_policy": "order"})
        cls.product_6.write({"commission_free": True, "invoice_policy": "order"})
        cls.product_template_4 = cls.env.ref(
            "product.product_product_4_product_template"
        )  # Customizable Desk (CONFIG)
        cls.product_template_4.write({"invoice_policy": "order"})
        cls.pt_11 = cls.env.ref("product.product_product_11_product_template")
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
        cls.demo_crr_item_1 = cls.env.ref(
            "sale_commission_product_criteria_domain.demo_crr_item_1"
        )
        cls.demo_cig_spain = cls.env.ref(
            "sale_commission_product_criteria_domain.demo_cig_spain"
        )
        cls.demo_cig_italy = cls.env.ref(
            "sale_commission_product_criteria_domain.demo_cig_italy"
        )
        cls.demo_agent_rules_restricted_italy = cls.env.ref(
            "sale_commission_product_criteria_domain.demo_agent_rules_restricted_italy"
        )
        cls.demo_agent_rules_restricted_spain = cls.env.ref(
            "sale_commission_product_criteria_domain.demo_agent_rules_restricted_spain"
        )
        cls.demo_commission_rules_restrict = cls.env.ref(
            "sale_commission_product_criteria_domain.demo_commission_rules_restrict"
        )
        cls.demo_commission_rules = cls.env.ref(
            "sale_commission_product_criteria.demo_commission_rules"
        )
        cls.demo_commission = cls.env.ref("sale_commission.demo_commission")
        cls.conf_chair_config_id = cls.env.ref(
            "product.product_product_11_product_template"
        )
        cls.cia_azure = cls.env.ref("sale_commission_product_criteria_domain.cia_azure")
        cls.res_partner_tiny_sale_agent = cls.env.ref(
            "sale_commission.res_partner_tiny_sale_agent"
        )

    def test_commission_domain_demo_cases(self):
        # Azure Spain Office furn. - Category
        so = self._create_sale_order(self.product_5, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.fixed_amount, 20)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 20)

        # Azure Spain Customizable Desk (CONFIG) - Product Template
        so = self._create_sale_order(
            self.product_template_4.product_variant_id, self.azure
        )
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.percent_amount, 5)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 50)

        # Azure Spain Variant: Customizable Desk (CONFIG) (Steel, White) - Variant
        so = self._create_sale_order(self.product_4, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.percent_amount, 15)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 150)

        # Deco Italy - All products
        so = self._create_sale_order(self.product_product_25, self.deco)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.fixed_amount, 10)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 10)

    def test_commission_domain(self):
        # group must have commission of CI
        self.demo_crr_item_1.group_id.commission_ids = False
        self.demo_crr_item_1.write({"sequence": 2})
        self.assertTrue(self.demo_crr_item_1.group_id.commission_ids)

        # count related agents
        self.demo_cig_italy._compute_agents_count()
        # self.assertEqual(demo_cig_italy.agents_count, 1)

        # if commission is not type of restricted then CI must have no group
        self.demo_crr_item_1.commission_id = self.demo_commission_rules
        self.demo_crr_item_1.write({"sequence": 3})
        self.assertFalse(self.demo_crr_item_1.group_id)

        # commission.item.agent: check agent_group_ids computed properly
        self.cia_azure._compute_agent_group_ids()
        self.assertTrue(self.cia_azure.agent_group_ids)

        # commission.item.agent: check agent_group_ids is False when agent got no rules
        self.cia_azure.agent_id = self.res_partner_tiny_sale_agent
        self.cia_azure._compute_agent_group_ids()
        self.assertFalse(self.cia_azure.agent_group_ids)

        # false, when commission is not product_restricted
        self.res_partner_tiny_sale_agent.write(
            {
                "allowed_commission_group_ids": [(6, 0, self.demo_cig_spain.ids)],
            }
        )
        self.assertFalse(self.res_partner_tiny_sale_agent.allowed_commission_group_ids)

        # check some partners compute methods
        self.azure._onchange_agent_ids()
        self.azure._compute_allowed_commission_group_ids_domain()
        self.assertFalse(self.azure.allowed_commission_group_ids_domain)
        self.demo_agent_rules_restricted_italy._compute_allowed_commission_group_ids_domain()
        self.assertTrue(
            self.demo_agent_rules_restricted_italy.allowed_commission_group_ids_domain
        )

        # trigger window action
        action = self.demo_cig_spain.action_open_related_agents()
        self.assertEqual(type(action), dict)

        # you cant delete it having related CIs
        with self.assertRaises(exception=odoo.exceptions.ValidationError):
            self.demo_cig_spain.unlink()

        #
        self.env["commission.items.group"].create({"name": "Delete Me"}).unlink()

        # computes was modified to consider new commission type: product_restricted
        so = self._create_sale_order(self.product_4, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 150)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 150)

        #
        tst_partner = so.partner_id.copy({})
        tst_partner.commission_item_agent_ids = [(6, 0, self.demo_cig_italy.ids)]
        so.partner_id = tst_partner
        so.order_line.agent_ids.agent_id = self.demo_agent_rules_restricted_italy
        res = so.order_line.agent_ids._get_single_commission_amount(
            self.demo_commission_rules_restrict,
            1,
            self.conf_chair_config_id.product_variant_id,
            1,
        )
        self.assertEqual(res, 20)

        # computes was modified to consider new commission type: product_restricted
        self.demo_agent_rules_restricted_italy.commission_id = (
            self.demo_commission_rules_restrict
        )
        so = self._create_sale_order(self.product_5, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 20)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 20)

        # computes was modified to consider new commission type: product_restricted
        self.product_5.commission_free = True
        so = self._create_sale_order(self.product_5, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 0)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 0)

        # computes was modified to consider new commission type: product_restricted
        self.azure.agent_ids.commission_id = self.demo_commission_rules
        so = self._create_sale_order(self.product_6, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 0)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 0)

        # computes was modified to consider new commission type: product_restricted
        so = self._create_sale_order(self.product_1, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        invoice = self._invoice_sale_order(so)
        invoice.recompute_lines_agents()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 15)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 15)

        # discount net_amount percentage
        self.demo_agent_rules_restricted_spain.commission_id = (
            self.demo_commission_rules_restrict
        )
        self.azure.commission_item_agent_ids.group_ids = [
            (6, 0, self.demo_cig_spain.ids)
        ]
        so = self._create_sale_order(self.pt_11.product_variant_id, self.azure)
        so.order_line.discount = 20
        so.recompute_lines_agents()
        so.action_confirm()
        so.order_line.agent_ids.commission_id.item_ids.commission_type = "percentage"
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids.commission_id = self.demo_commission_rules_restrict
        invoice.line_ids.agent_ids.commission_id.amount_base_type = "net_amount"
        invoice.line_ids.agent_ids.commission_id.item_ids.commission_type = "percentage"
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 0)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 0)

        # no commission items
        self.demo_commission_rules_restrict.item_ids.unlink()
        so = self._create_sale_order(self.pt_11.product_variant_id, self.azure)
        so.recompute_lines_agents()
        so.action_confirm()
        so.order_line.agent_ids._compute_amount()
        invoice.line_ids.agent_ids._compute_amount()
        self.assertEqual(so.order_line.agent_ids.amount, 0)
        self.assertEqual(invoice.line_ids.agent_ids.amount, 0)

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
        wizard = self.advance_inv_model.create({"advance_payment_method": "delivered"})
        wizard.with_context(
            {
                "active_model": "sale.order",
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
            }
        ).create_invoices()
        invoice = sale_order.invoice_ids - old_invoices
        invoice.flush()
        return invoice
