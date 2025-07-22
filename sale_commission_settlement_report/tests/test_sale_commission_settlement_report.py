def test_showable_line_ids_filter(self):
    company = self.env.company
    settlement = self.env['commission.settlement'].create({...})
    line0 = self.env['commission.settlement.line'].create({
        'settlement_id': settlement.id,
        'settled_amount': 0.0,
    })
    line1 = self.env['commission.settlement.line'].create({
        'settlement_id': settlement.id,
        'settled_amount': 10.0,
    })

    company.settlement_skip_zero_amount_lines = False
    settlement._compute_showable_line_ids()
    self.assertEqual(settlement.showable_line_ids, settlement.line_ids)

    company.settlement_skip_zero_amount_lines = True
    settlement._compute_showable_line_ids()
    self.assertEqual(settlement.showable_line_ids, line1)
