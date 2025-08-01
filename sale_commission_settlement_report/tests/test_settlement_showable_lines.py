from odoo.tests.common import TransactionCase


class TestCommissionSettlementShowableLines(TransactionCase):
    def test_compute_showable_line_ids(self):
        Settlement = self.env["commission.settlement"]
        company = self.env.user.company_id

        # Create a new "commission.settlement" record in memory with two lines
        settlement = Settlement.new(
            {
                "company_id": company.id,
                "line_ids": [
                    (0, 0, {"settled_amount": 0.0}),
                    (0, 0, {"settled_amount": 42.0}),
                ],
            }
        )

        # Case 1: without filtering zero lines (flag = False)
        company.write({"settlement_skip_zero_amount_lines": False})
        settlement._compute_showable_line_ids()
        # Both lines are expected
        self.assertEqual(len(settlement.showable_line_ids), 2)
        amounts = settlement.showable_line_ids.mapped("settled_amount")
        # Compare amounts, order does not matter
        self.assertSetEqual(set(amounts), {0.0, 42.0})

        # Case 2: filter zero lines (flag = True) ---
        company.write({"settlement_skip_zero_amount_lines": True})
        settlement._compute_showable_line_ids()
        # Only the 42.0 line should remain
        self.assertEqual(len(settlement.showable_line_ids), 1)
        # On a recordset with a single element, .settled_amount returns the value
        self.assertEqual(settlement.showable_line_ids.settled_amount, 42.0)

        # Comparison of the related field
        self.assertEqual(
            settlement.show_partner_settlement_report,
            company.show_partner_settlement_report,
        )
