# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


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
        cls.contract = cls.env['contract.contract'].create(
            {
                'name': 'Test contract',
                'partner_id': cls.partner.id,
                'contract_type': 'sale',
            }
        )

        cls.contract_line = cls.env['contract.line'].create(
            {
                'contract_id': cls.contract.id,
                'product_id': cls.product.id,
                'name': cls.product.name,
                'quantity': 1.0,
                'uom_id': cls.product.uom_id.id,
                'price_unit': 10.0,
                'recurring_rule_type': 'monthly',
                'recurring_interval': 1,
                'date_start': '2018-01-01',
                'recurring_next_date': '2018-01-15',
                'is_auto_renew': False,
            }
        )

        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test account type',
            'type': 'other',
        })
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': cls.account_type.id
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
        })

        cls.invoice_line = cls.env['account.invoice.line'].create({
            'invoice_id': cls.invoice.id,
            'product_id': cls.product.id,
            'name': cls.product.name,
            'account_id': cls.account.id,
            'quantity': 1.0,
            'uom_id': cls.product.uom_id.id,
            'price_unit': 10.0,
        })

    def test_invoice_commissions(self):
        contracts = self.contract
        self.contract.recurring_create_invoice()
        invoice_lines = self.env['account.invoice.line'].search(
            [('contract_line_id', 'in',
              contracts.mapped('contract_line_ids').ids)]
        )
        self.assertEqual(len(invoice_lines), 1)
        self.assertEqual(len(invoice_lines.agents), 1)
        self.assertEqual(invoice_lines.agents.agent, self.agent)
        self.assertEqual(
            invoice_lines.agents.commission, self.commission)

    def test_invoice_wo_commissions(self):
        """Test correct creation when there's no agents"""
        contracts = self.contract
        self.partner.agents = False
        self.contract.recurring_create_invoice()
        invoice_lines = self.env['account.invoice.line'].search(
            [('contract_line_id', 'in',
              contracts.mapped('contract_line_ids').ids)]
        )
        self.assertEqual(len(invoice_lines), 1)
        self.assertFalse(invoice_lines.agents)

    def test_prepare_invoice_line(self):
        invoice_id = self.invoice
        invoice_values = self.invoice
        result = self.contract_line._prepare_invoice_line(
            invoice_id=invoice_id,
            invoice_values=invoice_values)
        self.assertEqual(result['agents'][0][2]['agent'], self.agent.id)
