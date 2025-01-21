# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

import dateutil.relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleCommissionDelegatePartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["commission"]
        cls.commission_net_invoice = cls.commission_model.create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.res_partner_model.create({"name": "Test Partner"})
        cls.partner.write({"agent": False})
        cls.settle_model = cls.env["commission.settlement"]
        cls.make_settle_model = cls.env["commission.make.settle"]
        cls.make_inv_model = cls.env["commission.make.invoice"]
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        cls.delegate_agent = cls.res_partner_model.create({"name": "Delegate Agent"})
        cls.agent_monthly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Monthly",
                "agent": True,
                "delegated_agent_id": cls.delegate_agent.id,
                "settlement": "monthly",
                "lang": "en_US",
            }
        )
        cls.agent_monthly_02 = cls.res_partner_model.create(
            {
                "name": "Test Agent 02 - Monthly",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
            }
        )

    def _create_invoice(self, agent, commission, date=None, currency=None):
        vals = {
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "agent_ids": [
                            (
                                0,
                                0,
                                {"agent_id": agent.id, "commission_id": commission.id},
                            )
                        ],
                    },
                )
            ],
        }
        if date:
            vals.update({"invoice_date": date, "date": date})
        if currency:
            vals.update({"currency_id": currency.id})
        move = self.env["account.move"].create([vals])
        move.action_post()
        return move

    def test_settlement(self):
        self._create_invoice(
            self.agent_monthly,
            self.commission_net_invoice,
        )
        self._create_invoice(
            self.agent_monthly_02,
            self.commission_net_invoice,
        )
        wizard = self.make_settle_model.create(
            {
                "date_to": (
                    fields.Datetime.from_string(fields.Datetime.now())
                    + dateutil.relativedelta.relativedelta(months=1)
                ),
                "settlement_type": "sale_invoice",
            }
        )
        wizard.action_settle()
        settlements = self.settle_model.search([("state", "=", "settled")])
        self.assertEqual(len(settlements), 2)
        self.env["commission.make.invoice"].with_context(
            settlement_ids=settlements.ids
        ).create(
            {
                "journal_id": self.journal.id,
                "product_id": self.product.id,
                "date": fields.Datetime.now(),
            }
        ).button_create()
        for settlement in settlements:
            self.assertEqual(settlement.state, "invoiced")
        settlement = settlements.filtered(lambda r: r.agent_id == self.agent_monthly)
        self.assertTrue(settlement)
        self.assertEqual(1, len(settlement))
        self.assertNotEqual(self.agent_monthly, settlement.invoice_id.partner_id)
        self.assertEqual(self.delegate_agent, settlement.invoice_id.partner_id)
        settlement = settlements.filtered(lambda r: r.agent_id == self.agent_monthly_02)
        self.assertTrue(settlement)
        self.assertEqual(1, len(settlement))
        self.assertEqual(self.agent_monthly_02, settlement.invoice_id.partner_id)
