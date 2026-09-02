# Copyright 2026 Zhintek - Juan C. Bonilla
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account_commission_oca.tests.test_account_commission import (
    TestAccountCommission,
)


@tagged("post_install", "-at_install")
class TestCommissionFormula(TestAccountCommission):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_formula = cls.commission_model.create(
            {
                "name": "Formula commission for tests",
                "commission_type": "formula",
                "formula": (
                    "result = 0\n"
                    "if self.object_id == line:\n"
                    "    result = line.price_subtotal * 0.05\n"
                ),
            }
        )

    def test_get_commission_amount_uses_formula_context(self):
        invoice = self._create_invoice(self.agent_monthly, self.commission_formula)
        line_agent = invoice.invoice_line_ids.agent_ids

        line_agent._compute_amount()

        expected = self.product.list_price * 0.05
        self.assertAlmostEqual(line_agent.amount, expected)

    def test_get_commission_amount_skips_formula_for_commission_free_product(self):
        self.product.commission_free = True
        commission = self.commission_model.create(
            {
                "name": "Formula commission skipped for free products",
                "commission_type": "formula",
                "formula": "result = 100.0",
            }
        )
        invoice = self._create_invoice(self.agent_monthly, commission)
        line_agent = invoice.invoice_line_ids.agent_ids

        line_agent._compute_amount()

        self.assertAlmostEqual(line_agent.amount, 0.0)
