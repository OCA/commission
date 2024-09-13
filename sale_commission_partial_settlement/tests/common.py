from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPartialSettlementCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["commission"]
        cls.partial_commission_net_paid = cls.commission_model.create(
            {
                "name": "20% fixed commission (Net amount) - Payment Based - Partial",
                "fix_qty": 20.0,
                "invoice_state": "paid",
                "amount_base_type": "net_amount",
                "payment_amount_type": "paid",
            }
        )
        cls.company = cls.env.ref("base.main_company")
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.write({"agent": False})
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.settle_model = cls.env["commission.settlement"]
        cls.make_settle_model = cls.env["commission.make.settle"]
        cls.make_inv_model = cls.env["commission.make.invoice"]
        cls.product = cls.env.ref("product.product_product_5")
        cls.product.list_price = 5  # for testing specific commission section
        cls.commission_product = cls.env["product.product"].create(
            {"name": "Commission test product", "type": "service"}
        )
        cls.product.write({"invoice_policy": "order"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        cls.agent_monthly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Monthly",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
                "commission_id": cls.partial_commission_net_paid.id,
            }
        )
        cls.income_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("account_type", "=", "income"),
            ],
            limit=1,
        )
        cls.commission_net_invoice = cls.commission_model.create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )
        cls.agent_biweekly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Bi-weekly",
                "agent": True,
                "settlement": "biweekly",
                "lang": "en_US",
                "commission_id": cls.commission_net_invoice.id,
            }
        )

    def _create_multi_line_sale_order(self, agent, commission):
        return self.sale_order_model.create(
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
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "price_unit": self.product.lst_price,
                            "agent_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "agent_id": self.agent_monthly.id,
                                        "commission_id": self.partial_commission_net_paid.id,
                                    },
                                )
                            ],
                        },
                    ),
                ],
            }
        )

    def _invoice_sale_order(self, sale_order):
        old_invoices = sale_order.invoice_ids
        wizard = self.advance_inv_model.create(
            {"advance_payment_method": "delivered", "sale_order_ids": [sale_order.id]}
        )
        wizard.with_context(
            **{
                "active_model": "sale.order",
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
            }
        ).create_invoices()
        invoice = sale_order.invoice_ids - old_invoices
        return invoice

    def _settle_agent(self, agent=None, period=None, date=None):
        vals = {
            "date_to": (
                (
                    fields.Datetime.from_string(fields.Datetime.now())
                    + relativedelta(months=period)
                )
                if period
                else date
            ),
            "settlement_type": "sale_invoice",
        }
        if agent:
            vals["agent_ids"] = [(4, agent.id)]
        wizard = self.make_settle_model.create(vals)
        wizard.action_settle()

    def register_payment(
        self,
        invoice,
        payment_date,
        amount=None,
        payment_difference_handling="reconcile",
    ):
        payment_model = self.env["account.payment.register"]
        invoice.action_post()
        if not amount:
            amount = invoice.amount_total
        ctx = {
            "active_model": "account.move",
            "active_ids": [invoice.id],
        }
        return (
            payment_model.with_context(**ctx)
            .create(
                {
                    "payment_date": payment_date,
                    "amount": amount,
                    "journal_id": self.env["account.journal"]
                    .search([("type", "=", "bank")], limit=1)
                    .id,
                    "payment_difference_handling": payment_difference_handling,
                }
            )
            .action_create_payments()
        )
