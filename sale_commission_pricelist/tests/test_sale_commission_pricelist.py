# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.account_commission.tests.test_account_commission import (
    TestAccountCommission,
)


class TestSaleCommissionPricelist(TestAccountCommission):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test commission pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "20% discount and commission on Test " "product 2",
                            "applied_on": "0_product_variant",
                            "product_id": cls.product.id,
                            "compute_price": "formula",
                            "base": "list_price",
                            "price_discount": 20,
                            "commission_id": cls.commission_section_paid.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "10%  Discount and commission",
                            "compute_price": "percentage",
                            "base": "list_price",
                            "percent_price": 10,
                            "applied_on": "3_global",
                            "commission_id": cls.commission_section_invoice.id,
                        },
                    ),
                ],
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test product2 for commissions",
                "list_price": 5,
            }
        )

    def _create_sale_order(self):
        agent = self.env.ref("commission.res_partner_pritesh_sale_agent")
        self.partner.agent_ids = [(6, 0, agent.ids)]
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        order_form.pricelist_id = self.pricelist
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product

        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product2

        order = order_form.save()

        return order

    def test_sale_commission_pricelist(self):
        sale_order = self._create_sale_order()
        self.assertEqual(
            sale_order.order_line[0].agent_ids[:1].commission_id,
            self.commission_section_paid,
        )
        self.assertEqual(
            sale_order.order_line[1].agent_ids[:1].commission_id,
            self.commission_section_invoice,
        )

    def test_prepare_agents_vals(self):
        commission_3 = self.env["commission"].create(
            {"name": "3% commission", "fix_qty": 3.0}
        )
        pricelist_3 = self.env["product.pricelist"].create(
            {
                "name": "Test commission pricelist 3",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "30% discount and commission on Test " "product 2",
                            "applied_on": "0_product_variant",
                            "product_id": self.product2.id,
                            "compute_price": "formula",
                            "base": "list_price",
                            "price_discount": 30,
                            "commission_id": commission_3.id,
                        },
                    ),
                ],
            }
        )
        # Nothing changes
        sale_order = self._create_sale_order()
        sale_order.pricelist_id = pricelist_3
        self.assertEqual(
            sale_order.order_line[1].agent_ids[:1].commission_id, commission_3
        )
