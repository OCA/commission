from odoo.tests.common import TransactionCase


class TestCommissionSettlementShowableLines(TransactionCase):
    def test_compute_showable_line_ids(self):
        Settlement = self.env["commission.settlement"]
        company = self.env.user.company_id

        agent = self.env["res.partner"].create(
            {"name": "Test Agent", "is_company": False}
        )
        currency = company.currency_id or self.env.ref("base.EUR")

        settlement = Settlement.create(
            {
                "agent_id": agent.id,
                "company_id": company.id,
                "currency_id": currency.id,
                "date_from": "2025-08-01",
                "date_to": "2025-08-31",
                "settlement_type": "manual",
                "line_ids": [
                    (0, 0, {"settled_amount": 0.0}),
                    (0, 0, {"settled_amount": 42.0}),
                ],
            }
        )

        # Case 1: without filtering zero lines (flag = False)
        company.write({"settlement_skip_zero_amount_lines": False})
        settlement._compute_showable_line_ids()
        self.assertEqual(len(settlement.showable_line_ids), 2)
        amounts = settlement.showable_line_ids.mapped("settled_amount")
        self.assertSetEqual(set(amounts), {0.0, 42.0})

        # Case 2: filter zero lines (flag = True) ---
        company.write({"settlement_skip_zero_amount_lines": True})
        settlement._compute_showable_line_ids()
        self.assertEqual(len(settlement.showable_line_ids), 1)
        self.assertEqual(settlement.showable_line_ids.settled_amount, 42.0)

        self.assertEqual(
            settlement.show_partner_settlement_report,
            company.show_partner_settlement_report,
        )
