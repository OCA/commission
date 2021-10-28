# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

import dateutil.relativedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestSaleCommissionDelegatePartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["sale.commission"]
        cls.commission_net_invoice = cls.commission_model.create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.write({"agent": False})
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.settle_model = cls.env["sale.commission.settlement"]
        cls.make_settle_model = cls.env["sale.commission.make.settle"]
        cls.make_inv_model = cls.env["sale.commission.make.invoice"]
        cls.product = cls.env.ref("product.product_product_5")
        cls.product.write({"invoice_policy": "order"})
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

    def _create_sale_order(self, agent, commission):
        sale_order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": self.product.lst_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": agent.id,
                                        "commission_id": commission.id,
                                    },
                                )
                            ],
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.invoice_ids), 0)
        payment = self.advance_inv_model.create({"advance_payment_method": "delivered"})
        context = {
            "active_model": "sale.order",
            "active_ids": [sale_order.id],
            "active_id": sale_order.id,
        }
        payment.with_context(context).create_invoices()
        self.assertEqual(len(sale_order.invoice_ids), 1)
        for invoice in sale_order.invoice_ids:
            invoice.post()
            self.assertEqual(invoice.state, "posted")

    def test_settlement(self):
        self._create_sale_order(
            self.agent_monthly, self.commission_net_invoice,
        )
        self._create_sale_order(
            self.agent_monthly_02, self.commission_net_invoice,
        )
        wizard = self.make_settle_model.create(
            {
                "date_to": (
                    fields.Datetime.from_string(fields.Datetime.now())
                    + dateutil.relativedelta.relativedelta(months=1)
                )
            }
        )
        wizard.action_settle()
        settlements = self.settle_model.search([("state", "=", "settled")])
        self.assertEqual(len(settlements), 2)
        self.env["sale.commission.make.invoice"].with_context(
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
