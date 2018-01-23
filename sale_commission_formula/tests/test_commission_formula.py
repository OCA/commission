# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase


class TestCommissionFormula(TransactionCase):

    def setUp(self):
        super(TestCommissionFormula, self).setUp()
        self.agent = self.env.ref('sale_commission_formula.agent1')
        self.commission = self.env.ref(
            'sale_commission_formula.commission_5perc10extra')
        self.sale_order = self.env.ref('sale_commission_formula.sale_order_1')
        self.so_line = self.env.ref(
            'sale_commission_formula.sale_order_line_1')
        self.agent_commissions = {
            'agent': self.agent.id, 'commission': self.commission.id}

    def test_sale_order_commission(self):
        # we test the '5% + 10% extra' we should return 41.25 since
        # the order total amount is 750.00.
        self.env['sale.order.line.agent'].create({
            'sale_line': self.so_line.id,
            'agent': self.agent.id,
            'commission': self.commission.id,
        })
        self.assertEqual(41.25, self.sale_order.commission_total)

    def test_invoice_commission(self):
        # we confirm the sale order and create the corresponding invoice
        self.sale_order.action_confirm()
        self.so_line.qty_delivered = self.so_line.product_uom_qty
        invoice_id = self.sale_order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        # we add the commissions on the first invoice line
        invoice_line = invoice.invoice_line_ids[0]
        self.env['account.invoice.line.agent'].create({
            'invoice_line': invoice_line.id,
            'agent': self.agent.id,
            'commission': self.commission.id,
        })
        # we test the '5% + 10% extra' commissions on the invoice too
        self.assertEqual(41.25, invoice.commission_total)

    def test_invoice_refund_commission(self):
        # we confirm the sale order and create the corresponding invoice
        self.sale_order.action_confirm()
        self.so_line.qty_delivered = self.so_line.product_uom_qty
        invoice_id = self.sale_order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        # we add the commissions on the first invoice line
        invoice_line = invoice.invoice_line_ids[0]
        self.env['account.invoice.line.agent'].create({
            'invoice_line': invoice_line.id,
            'agent': self.agent.id,
            'commission': self.commission.id,
        })
        # we test the '5% + 10% extra' commissions on the invoice too
        self.assertEqual(41.25, invoice.commission_total)
        invoice.action_invoice_open()
        self.env['account.invoice.refund'].create({
            'filter_refund': 'cancel',
            'description': 'Wrong product',
        }).with_context(active_ids=invoice.id).invoice_refund()
        self.assertEqual(-41.25,
                         invoice.refund_invoice_ids[0].commission_total)
