# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form, tagged

from odoo.addons.commission.tests.test_commission import TestCommissionBase


@tagged("post_install", "-at_install")
class TestAccountCommissionPaymentSettlement(TestCommissionBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_net_paid.invoice_state = "paid"
        cls.purchase_journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.payment_journal = cls.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product for commissions", "list_price": 100}
        )
        cls.today = fields.Date.context_today(cls.env.user)
        cls.next_month = cls.today + relativedelta(months=1)

    def _create_invoice(self, agent, commission, date):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = self.partner
        invoice_form.invoice_date = date
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
        invoice = invoice_form.save()
        invoice.invoice_line_ids.agent_ids = [
            (0, 0, {"agent_id": agent.id, "commission_id": commission.id})
        ]
        invoice.action_post()
        return invoice

    def _register_payment(self, invoice, date):
        self.env["account.payment.register"].with_context(
            active_ids=invoice.ids, active_model="account.move"
        ).create(
            {"journal_id": self.payment_journal.id, "payment_date": date}
        ).action_create_payments()

    def _remove_payment(self, invoice):
        """Remove the payment from the invoice payment widget."""
        partial = invoice.line_ids.matched_credit_ids
        invoice.js_remove_outstanding_partial(partial.id)

    def _settle(self, agent, date_to):
        wizard_form = Form(self.make_settle_model)
        wizard_form.settlement_type = "sale_invoice"
        wizard_form.date_to = date_to
        wizard_form.agent_ids.add(agent)
        wizard_form.save().action_settle()
        return self.settle_model.search(
            [("agent_id", "=", agent.id), ("state", "!=", "cancel")]
        )

    def test_settle_past_period_without_later_payments(self):
        invoice_paid_in_period = self._create_invoice(
            self.agent_monthly, self.commission_net_paid, "2024-01-10"
        )
        invoice_paid_later = self._create_invoice(
            self.agent_monthly, self.commission_net_paid, "2024-01-10"
        )
        self._register_payment(invoice_paid_in_period, "2024-01-20")
        self._register_payment(invoice_paid_later, "2024-02-15")
        settlement = self._settle(self.agent_monthly, "2024-02-10")
        self.assertEqual(
            settlement.line_ids.invoice_line_id.move_id, invoice_paid_in_period
        )
        self.assertEqual(self._settle(self.agent_monthly, "2024-03-10"), settlement)
        self.assertEqual(
            settlement.line_ids.invoice_line_id.move_id,
            invoice_paid_in_period + invoice_paid_later,
        )

    def test_settle_payment_by_due_date(self):
        """A payment collected after its date, as a payment order confirmed in
        advance, counts on its due date.
        """
        invoice = self._create_invoice(
            self.agent_monthly, self.commission_net_paid, "2024-01-10"
        )
        entry_form = Form(
            self.env["account.move"].with_context(default_move_type="entry")
        )
        entry_form.date = "2024-01-20"
        with entry_form.line_ids.new() as line_form:
            line_form.account_id = self.payment_journal.default_account_id
            line_form.debit = invoice.amount_total
        with entry_form.line_ids.new() as line_form:
            line_form.account_id = invoice.partner_id.property_account_receivable_id
            line_form.partner_id = invoice.partner_id
            line_form.credit = invoice.amount_total
            line_form.date_maturity = "2024-02-15"
        entry = entry_form.save()
        entry.action_post()
        receivable_line = entry.line_ids.filtered("credit")
        invoice.js_assign_outstanding_line(receivable_line.id)
        self.assertEqual(invoice.payment_state, "paid")
        self.assertFalse(self._settle(self.agent_monthly, "2024-02-10"))
        settlement = self._settle(self.agent_monthly, "2024-03-10")
        self.assertEqual(settlement.line_ids.invoice_line_id.move_id, invoice)

    def test_payment_undone_and_paid_again(self):
        invoice = self._create_invoice(
            self.agent_monthly, self.commission_net_paid, "2024-01-10"
        )
        agent_line = invoice.invoice_line_ids.agent_ids
        amount = agent_line.amount
        self.assertTrue(amount)
        self._register_payment(invoice, "2024-01-20")
        settlement = self._settle(self.agent_monthly, "2024-02-10")
        self.assertEqual(settlement.total, amount)
        settlement.make_invoices(self.purchase_journal, self.commission_product)
        self._remove_payment(invoice)
        self.assertEqual(agent_line.payment_reversal_date, self.today)
        self.assertEqual(agent_line.pending_amount, -amount)
        # The payment was undone after this date limit
        self.assertEqual(self._settle(self.agent_monthly, "2024-03-10"), settlement)
        settlements = self._settle(self.agent_monthly, self.next_month)
        reversal_settlement = settlements - settlement
        self.assertEqual(reversal_settlement.line_ids.settled_amount, -amount)
        self.assertEqual(reversal_settlement.line_ids.date, self.today)
        self.assertFalse(agent_line.pending_amount)
        self.assertEqual(
            agent_line.settlement_line_ids.settlement_id,
            settlement + reversal_settlement,
        )
        self._register_payment(invoice, self.today)
        self.assertEqual(agent_line.pending_amount, amount)
        self._settle(self.agent_monthly, self.next_month)
        self.assertEqual(reversal_settlement.total, 0)
        self.assertFalse(agent_line.pending_amount)

    def test_cancel_reversal_settlement(self):
        invoice = self._create_invoice(
            self.agent_monthly, self.commission_net_paid, "2024-01-10"
        )
        agent_line = invoice.invoice_line_ids.agent_ids
        self._register_payment(invoice, "2024-01-20")
        settlement = self._settle(self.agent_monthly, "2024-02-10")
        settlement.make_invoices(self.purchase_journal, self.commission_product)
        self._remove_payment(invoice)
        reversal_settlement = (
            self._settle(self.agent_monthly, self.next_month) - settlement
        )
        reversal_settlement.action_cancel()
        self.assertEqual(agent_line.pending_amount, -agent_line.amount)
        settlements = self._settle(self.agent_monthly, self.next_month)
        self.assertEqual((settlements - settlement).total, -agent_line.amount)

    def test_invoice_based_commission_not_reversed(self):
        commission = self.commission_net_paid.copy({"invoice_state": "open"})
        invoice = self._create_invoice(self.agent_monthly, commission, "2024-01-10")
        agent_line = invoice.invoice_line_ids.agent_ids
        self._register_payment(invoice, "2024-01-20")
        settlement = self._settle(self.agent_monthly, "2024-02-10")
        self._remove_payment(invoice)
        self.assertFalse(agent_line.pending_amount)
        self.assertFalse(agent_line.payment_reversal_date)
        self.assertEqual(self._settle(self.agent_monthly, self.next_month), settlement)
