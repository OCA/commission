# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
import dateutil.relativedelta


class TestSaleCommission(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestSaleCommission, self).setUp()
        self.commission_model = self.env['sale.commission']
        self.commission_net_paid = self.commission_model.create({
            'name': '20% fixed commission (Net amount) - Payment Based',
            'fix_qty': 20.0,
            'invoice_state': 'paid',
            'amount_base_type': 'net_amount',
        })
        self.commission_net_invoice = self.commission_model.create({
            'name': '10% fixed commission (Net amount) - Invoice Based',
            'fix_qty': 10.0,
            'amount_base_type': 'net_amount',
        })
        self.commission_section_paid = self.commission_model.create({
            'name': 'Section commission - Payment Based',
            'commission_type': 'section',
            'invoice_state': 'paid',
            'sections': [(0, 0, {
                'amount_from': 1.0,
                'amount_to': 100.0,
                'percent': 10.0,
            })],
            'amount_base_type': 'net_amount',
        })
        self.commission_section_invoice = self.commission_model.create({
            'name': 'Section commission - Invoice Based',
            'commission_type': 'section',
            'sections': [(0, 0, {
                'amount_from': 15000.0,
                'amount_to': 16000.0,
                'percent': 20.0,
            })]
        })
        self.res_partner_model = self.env['res.partner']
        self.partner = self.browse_ref('base.res_partner_2')
        self.partner.write({'supplier': False, 'agent': False})
        self.sale_order_model = self.env['sale.order']
        self.advance_inv_model = self.env['sale.advance.payment.inv']
        self.settle_model = self.env['sale.commission.settlement']
        self.make_settle_model = self.env['sale.commission.make.settle']
        self.make_inv_model = self.env['sale.commission.make.invoice']
        self.product = self.browse_ref('product.product_product_5')
        self.product.write({
            'invoice_policy': 'order',
        })
        self.journal = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1
        )
        self.agent_monthly = self.res_partner_model.create({
            'name': 'Test Agent - Monthly',
            'agent': True,
            'settlement': 'monthly',
            'lang': 'en_US',
        })
        self.agent_quaterly = self.res_partner_model.create({
            'name': 'Test Agent - Quaterly',
            'agent': True,
            'settlement': 'quaterly',
            'lang': 'en_US',
        })
        self.agent_semi = self.res_partner_model.create({
            'name': 'Test Agent - Semi-annual',
            'agent': True,
            'settlement': 'semi',
            'lang': 'en_US',
        })
        self.agent_annual = self.res_partner_model.create({
            'name': 'Test Agent - Annual',
            'agent': True,
            'settlement': 'annual',
            'lang': 'en_US',
        })

    def _create_sale_order(self, agent, commission):
        return self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'product_uom': self.ref('product.product_uom_unit'),
                'price_unit': self.product.lst_price,
                'agents': [(0, 0, {
                    'agent': agent.id,
                    'commission': commission.id
                })]
            })]
        })

    def test_sale_commission_gross_amount_payment(self):
        self.check_full(
            self.browse_ref('sale_commission.res_partner_pritesh_sale_agent'),
            self.commission_section_paid,
            1
        )

    def test_sale_commission_gross_amount_payment_annual(self):
        self.check_full(
            self.agent_annual,
            self.commission_section_paid,
            12
        )

    def test_sale_commission_gross_amount_payment_semi(self):
        self.check_full(
            self.agent_semi,
            self.commission_section_paid,
            6
        )

    def check_full(self, agent, commission, period):
        sale_order = self._create_sale_order(
            agent,
            commission
        )
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.invoice_ids), 0)
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context = {"active_model": 'sale.order',
                   "active_ids": [sale_order.id],
                   "active_id": sale_order.id}
        payment.with_context(context).create_invoices()
        self.assertNotEqual(len(sale_order.invoice_ids), 0)
        for invoice in sale_order.invoice_ids:
            invoice.action_invoice_open()
            self.assertEqual(invoice.state, 'open')
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=period))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertEqual(len(settlements), 0)
        journals = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', sale_order.company_id.id)
        ], limit=1)
        for invoice in sale_order.invoice_ids:
            invoice.pay_and_reconcile(journals[:1], invoice.amount_total)
        self.assertTrue(sale_order.invoice_ids)
        self.assertEqual(sale_order.invoice_ids[:1].state, "paid")
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=period))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertNotEqual(len(settlements), 0)
        self.env['sale.commission.make.invoice'].with_context(
            settlement_ids=settlements.ids
        ).create({
            'journal': self.journal.id,
            'product': self.product.id,
            'date': fields.Datetime.now(),
        }).button_create()
        for settlement in settlements:
            self.assertEqual(settlement.state, 'invoiced')
        with self.assertRaises(UserError):
            settlements.action_cancel()
        with self.assertRaises(UserError):
            settlements.unlink()

    def test_sale_commission_gross_amount_invoice(self):
        sale_order = self._create_sale_order(
            self.agent_quaterly,
            self.browse_ref('sale_commission.demo_commission')
        )
        sale_order.action_confirm()
        self.assertEqual(
            len(sale_order.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context = {"active_model": 'sale.order',
                   "active_ids": [sale_order.id],
                   "active_id": sale_order.id}
        payment.with_context(context).create_invoices()
        for invoice in sale_order.invoice_ids:
            invoice.action_invoice_open()
            self.assertEqual(invoice.state, 'open')
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        wizard2 = self.make_inv_model.create({
            'product': 1,
            'journal': self.journal.id,
        })
        wizard2.button_create()
        settlements = self.settle_model.search([('state', '=', 'invoiced')])
        for settlement in settlements:
            self.assertNotEqual(
                len(settlement.invoice), 0,
                "Settlements need to be in Invoiced State."
            )

    def test_sale_commission_net_amount_payment(self):
        sale_order = self._create_sale_order(
            self.agent_semi,
            self.commission_net_paid
        )
        sale_order.action_confirm()
        self.assertEqual(
            len(sale_order.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context = {"active_model": 'sale.order',
                   "active_ids": [sale_order.id],
                   "active_id": sale_order.id}
        payment.with_context(context).create_invoices()
        for invoice in sale_order.invoice_ids:
            invoice.action_invoice_open()
            self.assertEqual(invoice.state, 'open')
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        journals = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', sale_order.company_id.id)
        ], limit=1)
        for invoice in sale_order.invoice_ids:
            invoice.pay_and_reconcile(journals[:1], invoice.amount_total)
        self.assertNotEqual(
            len(sale_order.invoice_ids), 0, "Invoice should be created."
        )
        self.assertTrue(sale_order.invoice_ids, "Order is not invoiced.")
        self.assertEqual(sale_order.invoice_ids[:1].state, "paid")
        for invoice in sale_order.invoice_ids:
            refund_wiz = self.env['account.invoice.refund'].with_context(
                active_ids=invoice.ids, active_id=invoice.id
            ).create({
                'description': 'Refund test',
                'filter_refund': 'refund',
            })
            refund_wiz.invoice_refund()

    def test_sale_commission_section_payment(self):
        sale_order = self._create_sale_order(
            self.browse_ref('sale_commission.res_partner_pritesh_sale_agent'),
            self.commission_section_paid
        )
        sale_order.action_confirm()
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        payment.with_context(active_model='sale.order',
                             active_ids=[sale_order.id],
                             active_id=sale_order.id).create_invoices()
        self.assertNotEqual(
            len(sale_order.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        for invoice in sale_order.invoice_ids:
            invoice.action_invoice_open()
            self.assertEqual(invoice.state, 'open')
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertEqual(
            len(settlements), 0,
            "The Type of Commission only allows create the Settlements when"
            " the Invoices are Paid.")
        journals = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', sale_order.company_id.id)
        ], limit=1)
        for invoice in sale_order.invoice_ids:
            invoice.pay_and_reconcile(journals[:1], invoice.amount_total)
        self.assertNotEqual(
            len(sale_order.invoice_ids), 0, "Invoice should be created."
        )
        self.assertTrue(sale_order.invoice_ids, "Order is not invoiced.")
        self.assertEqual(sale_order.invoice_ids[:1].state, "paid")

    def test_sale_commission_section_invoice(self):
        sale_order = self._create_sale_order(
            self.browse_ref('sale_commission.res_partner_pritesh_sale_agent'),
            self.commission_section_invoice
        )
        sale_order.action_confirm()
        self.assertEqual(
            len(sale_order.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context = {"active_model": 'sale.order',
                   "active_ids": [sale_order.id],
                   "active_id": sale_order.id}
        payment.with_context(context).create_invoices()
        for invoice in sale_order.invoice_ids:
            invoice.action_invoice_open()
            self.assertEqual(invoice.state, 'open')
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        wizard2 = self.make_inv_model.create({
            'product': 1,
            'journal': self.journal.id
        })
        wizard2.button_create()
        settlements = self.settle_model.search([('state', '=', 'invoiced')])
        for settlement in settlements:
            self.assertNotEqual(
                len(settlement.invoice), 0,
                "Settlements need to be in Invoiced State."
            )

    def test_res_partner_onchange(self):
        self.assertFalse(self.partner.supplier)
        self.assertFalse(self.partner.agent)
        self.partner.agent = True
        self.partner.onchange_agent_type()
        self.assertTrue(self.partner.supplier)

    def test_sale_default_agent(self):
        sale_agent = self.browse_ref(
            'sale_commission.res_partner_pritesh_sale_agent')
        self.partner.agents = [(6, 0, [sale_agent.id])]
        saleorder = self.sale_order_model.with_context(
            partner_id=self.partner.id).create({
                'partner_id': self.partner.id,
                'order_line': [(0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 8.0,
                    'product_uom': self.ref('product.product_uom_unit'),
                })],
            })
        self.assertNotEqual(
            len(saleorder.mapped('order_line.agents')), 0,
            "There should be a agent assigned to the lines."
        )
        self.assertTrue(
            sale_agent in saleorder.mapped('order_line.agents.agent'),
            "Sale agent in partner should be assigned in lines.")

    def test_wrong_section(self):
        with self.assertRaises(ValidationError):
            self.commission_model.create({
                'name': 'Section commission - Invoice Based',
                'commission_type': 'section',
                'sections': [(0, 0, {
                    'amount_from': 5,
                    'amount_to': 1,
                    'percent': 20.0,
                })],
            })

    def test_sale_order_onchange_partner(self):
        sale_order = self._create_sale_order(
            self.browse_ref('sale_commission.res_partner_pritesh_sale_agent'),
            self.commission_section_invoice
        )
        partner = self.browse_ref('base.res_partner_12')
        partner.agent = False
        self.agent_annual.commission = self.commission_net_invoice
        partner.agents = self.agent_annual
        sale_order.partner_id = partner
        sale_order.onchange_partner_id()
        for line in sale_order.order_line:
            self.assertFalse(line.agents)
        sale_order.recompute_lines_agents()
        for line in sale_order.order_line:
            self.assertTrue(line.agents)
        sale_order.fiscal_position_id = self.env[
            'account.fiscal.position'].search([], limit=1)
        sale_order._compute_tax_id()
        for line in sale_order.order_line:
            self.assertFalse(line.agents)

    def test_invoice(self):
        self.partner.agent = False
        self.partner.agents = self.agent_semi
        partner = self.browse_ref('base.res_partner_12')
        partner.agent = False
        self.agent_annual.commission = self.commission_net_invoice
        partner.agents = self.agent_annual
        self.agent_semi.commission = self.commission_net_paid
        self.partner.agents = self.agent_semi
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id
        })
        line = self.env['account.invoice.line'].new({
            'invoice_id': invoice.id,
            'product_id': self.product.id,
            'product_uom_qty': 1.0,
            'product_uom': self.ref('product.product_uom_unit'),

        })
        line._onchange_product_id()
        line = self.env['account.invoice.line'].with_context({
            'partner_id': self.partner.id
        }).create(line._cache)
        self.assertGreater(len(line.agents), 0)
        invoice.partner = partner
        invoice._onchange_partner_id()
        self.assertEqual(len(line.agents), 0)
        invoice.recompute_lines_agents()
        self.assertGreater(len(line.agents), 0)
        invoice.journal_id = self.env['account.journal'].create({
            'name': 'TEST',
            'code': 'T',
            'type': 'sale',
        })
        invoice._onchange_journal_id()
        self.assertEqual(len(line.agents), 0)
        invoice.recompute_lines_agents()
        self.assertGreater(len(line.agents), 0)
        for agent in line.agents:
            agent.agent = self.agent_semi
            agent.onchange_agent()
            self.assertEqual(self.agent_semi.commission, agent.commission)

    def test_check_new_invoice_with_settle_invoiced(self):
        self.check_new_invoice_with_settle_invoiced(
            self.agent_monthly,
            self.commission_section_invoice,
            1
        )

    def check_new_invoice_with_settle_invoiced(self, agent, commission,
                                               period):
        sale_order = self._create_sale_order(
            agent,
            commission
        )
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.invoice_ids), 0)
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context = {"active_model": 'sale.order',
                   "active_ids": [sale_order.id],
                   "active_id": sale_order.id}
        payment.with_context(context).create_invoices()
        self.assertEqual(len(sale_order.invoice_ids), 1)
        for invoice in sale_order.invoice_ids:
            invoice.action_invoice_open()
            self.assertEqual(invoice.state, 'open')
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=period))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertEqual(len(settlements), 1)
        self.env['sale.commission.make.invoice'].with_context(
            settlement_ids=settlements.ids
        ).create({
            'journal': self.journal.id,
            'product': self.product.id,
            'date': fields.Datetime.now(),
        }).button_create()
        for settlement in settlements:
            self.assertEqual(settlement.state, 'invoiced')
        # create new invoice
        sale_order2 = self._create_sale_order(
            agent,
            commission
        )
        sale_order2.action_confirm()
        self.assertEqual(len(sale_order2.invoice_ids), 0)
        payment2 = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context2 = {"active_model": 'sale.order',
                    "active_ids": [sale_order2.id],
                    "active_id": sale_order2.id}
        payment2.with_context(context2).create_invoices()
        self.assertEqual(len(sale_order2.invoice_ids), 1)
        for invoice in sale_order2.invoice_ids:
            invoice.action_invoice_open()
            self.assertEqual(invoice.state, 'open')
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=period))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', 'in', ['settled',
                                                                 'invoiced'])])
        self.assertEqual(len(settlements), 2)
