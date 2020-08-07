# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestSaleCommissionSalesman(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product 1", "list_price": 100,}
        )
        SaleCommission = cls.env["sale.commission"]
        cls.commission_1 = SaleCommission.create(
            {"name": "1% commission", "fix_qty": 1.0,}
        )
        Partner = cls.env["res.partner"]
        cls.salesman = cls.env["res.users"].create(
            {"name": "Test agent", "login": "sale_comission_salesman_test",}
        )
        cls.agent = cls.salesman.partner_id
        cls.agent.write(
            {
                "agent": True,
                "salesman_as_agent": True,
                "commission": cls.commission_1.id,
            }
        )
        cls.other_agent = Partner.create(
            {
                "name": "Test other agent",
                "agent": True,
                "commission": cls.commission_1.id,
            }
        )
        cls.partner = Partner.create({"name": "Partner test",})
        cls.sale_order = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "user_id": cls.salesman.id,}
        )
        cls.invoice = cls.env["account.invoice"].create(
            {"partner_id": cls.partner.id, "user_id": cls.salesman.id,}
        )

    def test_check_salesman_commission(self):
        with self.assertRaises(exceptions.ValidationError):
            self.agent.commission = False

    def test_sale_commission_salesman(self):
        line = (
            self.env["sale.order.line"]
            .with_context(partner_id=self.partner.id)
            .create({"order_id": self.sale_order.id, "product_id": self.product.id,})
        )
        self.assertTrue(line.agents)
        self.assertTrue(line.agents.agent, self.agent)
        self.assertTrue(line.agents.commission, self.commission_1)

    def test_sale_commission_salesman_no_population(self):
        self.partner.agents = [(4, self.other_agent.id)]
        line = (
            self.env["sale.order.line"]
            .with_context(partner_id=self.partner.id)
            .create({"order_id": self.sale_order.id, "product_id": self.product.id,})
        )
        self.assertTrue(len(line.agents), 1)
        self.assertTrue(line.agents.agent, self.other_agent)

    def test_invoice_commission_salesman(self):
        line_obj = self.env["account.invoice.line"]
        line = line_obj.with_context(partner_id=self.partner.id).create(
            {
                "invoice_id": self.invoice.id,
                "product_id": self.product.id,
                "account_id": line_obj.get_invoice_line_account(
                    self.invoice.type, self.product, False, self.invoice.company_id
                ).id,
                "name": self.product.name,
                "price_unit": 1,
            }
        )
        self.assertTrue(line.agents)
        self.assertTrue(line.agents.agent, self.agent)
        self.assertTrue(line.agents.commission, self.commission_1)

    def test_invoice_commission_salesman_no_population(self):
        self.partner.agents = [(4, self.other_agent.id)]
        line_obj = self.env["account.invoice.line"]
        line = line_obj.with_context(partner_id=self.partner.id).create(
            {
                "invoice_id": self.invoice.id,
                "product_id": self.product.id,
                "account_id": line_obj.get_invoice_line_account(
                    self.invoice.type, self.product, False, self.invoice.company_id
                ).id,
                "name": self.product.name,
                "price_unit": 1,
            }
        )
        self.assertTrue(len(line.agents), 1)
        self.assertTrue(line.agents.agent, self.other_agent)
