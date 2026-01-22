# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleCommissionProductCriteriaPriceCompliance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create commission
        cls.commission = cls.env["commission"].create(
            {
                "name": "Test Commission",
                "commission_type": "product",
                "item_ids": [
                    # Inverse order to test non secuencial items
                    Command.create(
                        {
                            "sequence": 1,
                            "applied_on": "3_global",
                            "price_compliance_tier": "t2",
                            "commission_type": "fixed",
                            "fixed_amount": 5.0,
                        }
                    ),
                    Command.create(
                        {
                            "sequence": 2,
                            "applied_on": "3_global",
                            "price_compliance_tier": "t1",
                            "commission_type": "fixed",
                            "fixed_amount": 10.0,
                        }
                    ),
                ],
            }
        )
        # Create partner and agent
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.agent = cls.env["res.partner"].create(
            {
                "name": "Test Agent",
                "is_company": True,
                "agent": True,
                "agent_type": "agent",
                "commission_id": cls.commission.id,
                "settlement": "monthly",
            }
        )
        # Create product with Price Compliance
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "list_price": 100.0,
                "use_price_compliance_threshold": True,
                "price_compliance_threshold_t1": 0.1,  # 10%
                "price_compliance_threshold_t2": 0.2,  # 20%
                "price_compliance_threshold_t3": 0.0,  # Not used
            }
        )

    def _create_sale_order(self, partner, product):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [Command.create({"product_id": product.id})],
                "user_id": False,
            }
        )

    def test_commission_price_compliance_tiers(self):
        sale = self._create_sale_order(self.partner, self.product)
        sale.recompute_lines_agents()
        # Clear agents
        sale.order_line.agent_ids.unlink()
        # Create sale order line agent and let recomputation happens
        self.env["sale.order.line.agent"].create(
            {
                "object_id": sale.order_line.id,
                "agent_id": self.agent.id,
            }
        )
        # Commision Item Tier 1 discount
        sale.order_line.discount = 5.0
        sale.recompute_lines_agents_amount()
        self.assertEqual(sale.order_line.price_compliance_tier, "t1")
        self.assertEqual(sale.order_line.agent_ids.amount, 10.0)
        # Commision Item Tier 2 discount
        sale.order_line.discount = 15.0
        sale.recompute_lines_agents_amount()
        self.assertEqual(sale.order_line.price_compliance_tier, "t2")
        self.assertEqual(sale.order_line.agent_ids.amount, 5.0)
        # No item defined for Non Compliance Tier
        sale.order_line.discount = 25.0
        sale.recompute_lines_agents_amount()
        self.assertEqual(sale.order_line.price_compliance_tier, "non_compliant")
        self.assertEqual(sale.order_line.agent_ids.amount, 0.0)
