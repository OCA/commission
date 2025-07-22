def test_showable_line_ids_filter(self):
    company = self.env.company
    settlement = self.env["commission.settlement"].create({...})
    line_zero = self.env["commission.settlement.line"].create(
        {
            "settlement_id": settlement.id,
            "settled_amount": 0.0,
        }
    )
    line_pos = self.env["commission.settlement.line"].create(
        {
            "settlement_id": settlement.id,
            "settled_amount": 10.0,
        }
    )

    company.settlement_skip_zero_amount_lines = False
    settlement._compute_showable_line_ids()
    self.assertIn(line_zero, settlement.showable_line_ids)
    self.assertIn(line_pos, settlement.showable_line_ids)

    company.settlement_skip_zero_amount_lines = True
    settlement._compute_showable_line_ids()
    self.assertNotIn(line_zero, settlement.showable_line_ids)
    self.assertIn(line_pos, settlement.showable_line_ids)
