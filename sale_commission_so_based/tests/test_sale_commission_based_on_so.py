# Copyright 2016-2022 Tecnativa - Pedro M. Baeza
from odoo import fields
from odoo.tests import Form, tagged
from odoo.addons.sale_commission.tests.test_sale_commission import TestSaleCommission


@tagged("post_install", "-at_install")
class TestSaleCommissionBasedOnSO(TestSaleCommission):

    def _settle_agent_sale_order(self, agent=None, period=None, date=None):
        vals = self._get_make_settle_vals(agent, period, date)
        vals["settlement_type"] = "sale_order"
        wizard = self.make_settle_model.create(vals)
        wizard.action_settle()

    def test_sale_commission_so_based(self):
        # Make sure user is in English
        self.env.user.lang = "en_US"
        sale_order = self._create_sale_order(
            self.env.ref("commission.res_partner_pritesh_sale_agent"),
            self.commission_section_invoice,
        )
        self.assertIn("1", sale_order.order_line[0].commission_status)
        self.assertNotIn("agents", sale_order.order_line[0].commission_status)

        sale_order.action_confirm()

        self._settle_agent_sale_order(
            self.env.ref("commission.res_partner_pritesh_sale_agent"),
            1,
            0,
        )

        settlement = self.settle_model.search([("state", "=", "settled")])
        self.assertEqual(len(settlement), 1)
        self.assertEqual(settlement.settlement_type, 'sale_order')

        self.assertTrue(sale_order.order_line.agent_ids.settled)

        self.assertEqual(fields.Date.today(), settlement.line_ids.date)
        self.assertTrue(settlement.line_ids.commission_id)
        self.assertEqual(settlement.line_ids.settled_amount, 0)
