# © 2025 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo.tests.common import SavepointCase


class TestSaleCommissionProductCriteriaMinimal(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule = cls.env.ref("sale_commission_product_criteria.demo_commission_rules")
        cls.items = [
            cls.env.ref(
                "sale_commission_product_criteria.demo_commission_rules_item_1"
            ),
            cls.env.ref(
                "sale_commission_product_criteria.demo_commission_rules_item_2"
            ),
            cls.env.ref(
                "sale_commission_product_criteria.demo_commission_rules_item_3"
            ),
            cls.env.ref(
                "sale_commission_product_criteria.demo_commission_rules_item_4"
            ),
        ]

    def test_item_name_computation(self):
        for item in self.items:
            item._compute_commission_item_name_value()
            self.assertTrue(isinstance(item.name, str))

    def test_sale_order_commission_applied(self):
        partner = self.env.ref("base.res_partner_12")
        product = self.env.ref("product.product_product_1")
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        so.recompute_lines_agents()
        so.action_confirm()
        self.assertTrue(so.order_line.agent_ids, "No s'ha aplicat cap agent a la línia")
