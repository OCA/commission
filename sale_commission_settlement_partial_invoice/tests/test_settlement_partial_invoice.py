#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.fields import first
from odoo.tools import dateutil

from odoo.addons.sale_commission.tests.test_common import TestCommon


class TestSettlementPartialInvoice (TestCommon):

    def _create_settlement_invoices(self):
        agent = self.agent_monthly
        agent_month_number = 1

        # Create sale order for agent
        sale_order = self._create_sale_order(
            agent,
            self.env.ref('sale_commission.demo_commission')
        )
        sale_order.action_confirm()

        # Create invoices for sale order
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context = {"active_model": 'sale.order',
                   "active_ids": [sale_order.id],
                   "active_id": sale_order.id}
        payment.with_context(context).create_invoices()
        for invoice in sale_order.invoice_ids:
            invoice.action_invoice_open()

        # Create settlement for sale order invoices
        now = fields.Datetime.from_string(fields.Datetime.now())
        agent_period = dateutil.relativedelta.relativedelta(
            months=agent_month_number)
        wizard = self.make_settle_model.create({
            'date_to': now + agent_period,
        })
        action_res = wizard.action_settle()
        settlements = self.env[action_res.get('res_model')] \
            .search(action_res.get('domain'))

        # Create invoices for settlement
        wiz_make_invoice = self.make_inv_model.create({
            'product': 1,
            'journal': self.journal.id,
        })
        wiz_make_invoice.button_create()

        # View invoices from settlement
        action_res = settlements.action_view_invoice()
        invoice_model = self.env[action_res.get('res_model')]
        if action_res.get('res_id'):
            invoices = invoice_model.browse(action_res.get('res_id'))
        elif action_res.get('domain'):
            invoices = invoice_model.search(action_res.get('domain'))
        else:
            raise Exception("Cannot get invoices from settlement's "
                            "view invoice action")
        return invoices, settlements

    def test_edit_invoice(self):
        """
        Generate an invoice from a settlement.
        Check that adding a line to the generated invoice does not change
        the settlement's invoiced amount.
        """
        # Arrange: create a settlement and invoice it
        invoices, settlements = self._create_settlement_invoices()

        # Pre-condition: settlement invoiced amount is equal
        # to freshly generated invoice's untaxed amount
        settlement_invoiced_amount = sum(s.invoiced_amount for s in settlements)
        self.assertEqual(
            settlement_invoiced_amount,
            sum(i.amount_untaxed for i in invoices),
        )

        # Act: add a line to the invoice
        invoice = first(invoices)
        invoice_line = first(invoice.invoice_line_ids)
        invoice_line.copy(default={
            'name': "Test adding invoice line to settlement's invoice",
        })

        # Assert: invoice amount has changed
        # but settlement's invoiced amount hasn't
        self.assertNotEqual(
            settlement_invoiced_amount,
            sum(i.amount_untaxed for i in invoices),
        )
        self.assertEqual(
            settlement_invoiced_amount,
            sum(s.invoiced_amount for s in settlements),
        )

    def test_invoice_again(self):
        """
        Generate an invoice from a settlement,
        decrease its amount and invoice again.

        Check that the settlement's invoiced amount is its total amount.
        """
        # Arrange: create a settlement and invoice it
        invoices, settlements = self._create_settlement_invoices()

        # Pre-condition: settlement invoiced amount is equal
        # to its total
        invoices_number = len(settlements.mapped('invoice_ids'))
        self.assertEqual(
            sum(s.invoiced_amount for s in settlements),
            sum(s.total for s in settlements),
        )

        # Act: half one line's amount and invoice again
        invoice = first(invoices)
        invoice_line = first(invoice.invoice_line_ids)
        invoice_line.price_unit = invoice_line.price_unit / 2
        wiz_make_invoice = self.make_inv_model.create({
            'product': 1,
            'journal': self.journal.id,
        })
        wiz_make_invoice.button_create()

        # Assert: there are more invoices but settlement's invoiced amount
        # is still equal to its total
        self.assertGreater(
            len(settlements.mapped('invoice_ids')),
            invoices_number,
        )
        self.assertEqual(
            sum(s.invoiced_amount for s in settlements),
            sum(s.total for s in settlements),
        )
