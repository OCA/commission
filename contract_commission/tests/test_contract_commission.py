# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestContractCommission(common.TransactionCase):

    def setUp(self):
        super(TestContractCommission, self).setUp()
        self.product = self.env.ref('product.product_product_5')
        self.commission = self.env['sale.commission'].create(
            {'name': 'Test',
             'commission_type': 'fixed',
             'fix_qty': 3.0})
        self.agent = self.env['res.partner'].create(
            {'name': 'Agent',
             'agent': True,
             'commission': self.commission.id})
        self.partner = self.env.ref('base.res_partner_1')
        self.contract = self.env['account.analytic.account'].create(
            {'partner_id': self.partner.id,
             'name': 'Test contract',
             'recurring_invoices': True,
             'state': 'draft',
             'type': 'normal',
             'recurring_invoice_line_ids': [
                 (0, 0, {
                     'product_id': self.product.id,
                     'name': self.product.name,
                     'quantity': 1.0,
                     'uom_id': self.product.uom_id.id,
                     'price_unit': 1.0,
                 })]}
        )
        self.partner.agents = [(6, 0, self.agent.ids)]

    def test_invoice_commissions(self):
        self.contract.recurring_create_invoice()
        invoice_lines = self.env['account.invoice.line'].search(
            [('account_analytic_id', '=', self.contract.id)])
        self.assertEqual(len(invoice_lines), 1)
        self.assertEqual(len(invoice_lines.agents), 1)
        self.assertEqual(invoice_lines.agents.agent, self.agent)
        self.assertEqual(
            invoice_lines.agents.commission, self.commission)
