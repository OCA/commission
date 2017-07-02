# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestContractCommission(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractCommission, cls).setUpClass()
        cls.product = cls.env.ref('product.product_product_5')
        cls.commission = cls.env['sale.commission'].create(
            {'name': 'Test',
             'commission_type': 'fixed',
             'fix_qty': 3.0})
        cls.agent = cls.env['res.partner'].create(
            {'name': 'Agent',
             'agent': True,
             'commission': cls.commission.id})
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'agents': [(6, 0, cls.agent.ids)],
        })
        cls.contract = cls.env['account.analytic.account'].create(
            {'partner_id': cls.partner.id,
             'name': 'Test contract',
             'recurring_invoices': True,
             'state': 'draft',
             'type': 'normal',
             'recurring_invoice_line_ids': [
                 (0, 0, {
                     'product_id': cls.product.id,
                     'name': cls.product.name,
                     'quantity': 1.0,
                     'uom_id': cls.product.uom_id.id,
                     'price_unit': 1.0,
                 })]}
        )

    def test_invoice_commissions(self):
        self.contract.recurring_create_invoice()
        invoice_lines = self.env['account.invoice.line'].search(
            [('account_analytic_id', '=', self.contract.id)])
        self.assertEqual(len(invoice_lines), 1)
        self.assertEqual(len(invoice_lines.agents), 1)
        self.assertEqual(invoice_lines.agents.agent, self.agent)
        self.assertEqual(
            invoice_lines.agents.commission, self.commission)

    def test_invoice_wo_commissions(self):
        """Test correct creation when there's no agents"""
        self.partner.agents = False
        self.contract.recurring_create_invoice()
        invoice_lines = self.env['account.invoice.line'].search(
            [('account_analytic_id', '=', self.contract.id)]
        )
        self.assertEqual(len(invoice_lines), 1)
        self.assertFalse(invoice_lines.agents)
