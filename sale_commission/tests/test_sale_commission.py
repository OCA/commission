# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import exceptions, fields
import openerp.tests.common as common
import datetime
import dateutil.relativedelta


class TestSaleCommission(common.TransactionCase):

    def setUp(self):
        super(TestSaleCommission, self).setUp()
        self.commission_model = self.env['sale.commission']
        commission_net_paid = self.commission_model.create({
            'name': '20% fixed commission (Net amount) - Payment Based',
            'fix_qty': 20.0,
            'invoice_state': 'paid',
            'amount_base_type': 'net_amount',
        })
        commission_net_invoice = self.commission_model.create({
            'name': '10% fixed commission (Net amount) - Invoice Based',
            'fix_qty': 10.0,
            'amount_base_type': 'net_amount',
        })
        commission_section_paid = self.commission_model.create({
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
        commission_section_invoice = self.commission_model.create({
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
        agent_quaterly = self.res_partner_model.create({
            'name': 'Test Agent - Quaterly',
            'agent': True,
            'settlement': 'quaterly',
            'lang': 'en_US',
        })
        agent_semi = self.res_partner_model.create({
            'name': 'Test Agent - Semi-annual',
            'agent': True,
            'settlement': 'semi',
            'lang': 'en_US',
        })
        agent_annual = self.res_partner_model.create({
            'name': 'Test Agent - Annual',
            'agent': True,
            'settlement': 'annual',
            'lang': 'en_US',
        })
        self.sale_order_model = self.env['sale.order']
        self.advance_inv_model = self.env['sale.advance.payment.inv']
        self.settle_model = self.env['sale.commission.settlement']
        self.make_settle_model = self.env['sale.commission.make.settle']
        self.make_inv_model = self.env['sale.commission.make.invoice']
        self.saleorder1 = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.ref('product.product_product_7'),
                'product_uom_qty': 8.0,
                'agents': [(0, 0, {
                    'agent': self.ref(
                        'sale_commission.res_partner_pritesh_sale_agent'),
                    'commission': self.ref(
                        'sale_commission.demo_commission_paid')
                })]
            })]
        })
        self.saleorder2 = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.ref('product.product_product_7'),
                'product_uom_qty': 16.0,
                'product_uom': self.ref('product.product_uom_dozen'),
                'agents': [(0, 0, {
                    'agent': agent_quaterly.id,
                    'commission': self.ref(
                        'sale_commission.demo_commission'),
                })]
            })]
        })
        self.saleorder3 = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.ref('product.product_product_7'),
                'product_uom_qty': 8.0,
                'agents': [(0, 0, {
                    'agent': agent_semi.id,
                    'commission': commission_net_paid.id,
                })]
            })]
        })
        self.saleorder4 = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.ref('product.product_product_7'),
                'product_uom_qty': 16.0,
                'product_uom': self.ref('product.product_uom_dozen'),
                'agents': [(0, 0, {
                    'agent': agent_annual.id,
                    'commission': commission_net_invoice.id,
                })]
            })]
        })
        self.saleorder5 = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.ref('product.product_product_7'),
                'product_uom_qty': 8.0,
                'agents': [(0, 0, {
                    'agent':  self.ref(
                        'sale_commission.res_partner_pritesh_sale_agent'),
                    'commission': commission_section_paid.id,
                })]
            })]
        })
        self.saleorder6 = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.ref('product.product_product_7'),
                'product_uom_qty': 16.0,
                'product_uom': self.ref('product.product_uom_dozen'),
                'agents': [(0, 0, {
                    'agent':  self.ref(
                        'sale_commission.res_partner_pritesh_sale_agent'),
                    'commission': commission_section_invoice.id,
                })]
            })]
        })

    def test_sale_commission_gross_amount_payment(self):
        self.saleorder1.signal_workflow('order_confirm')
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        payment.with_context(active_model='sale.order',
                             active_ids=[self.saleorder1.id],
                             active_id=self.saleorder1.id).create_invoices()
        self.assertNotEquals(
            len(self.saleorder1.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        for invoice in self.saleorder1.invoice_ids:
            invoice.date_invoice = fields.Date.today()
            invoice.signal_workflow('invoice_open')
        wizard = self.make_settle_model.create(
            {'date_to': (datetime.datetime.now() +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertEquals(
            len(settlements), 0,
            "The Type of Commission only allows create the Settlements when"
            " the Invoices are Paid.")
        journals = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', self.saleorder1.company_id.id)
        ], limit=1)
        for invoice in self.saleorder1.invoice_ids:
            invoice.pay_and_reconcile(
                invoice.amount_total, self.ref('account.cash'),
                self.ref('account.period_8'), journals[:1].id,
                self.ref('account.cash'), self.ref('account.period_8'),
                journals[:1].id, name='test')
        self.assertNotEquals(len(self.saleorder1.invoice_ids), 0,
                             "Invoice should be created.")
        self.assertTrue(self.saleorder1.invoice_exists,
                        "Order is not invoiced.")
        self.assertTrue(self.saleorder1.invoiced, "Order is not paid.")

    def test_sale_commission_gross_amount_invoice(self):
        self.saleorder2.signal_workflow('order_confirm')
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        payment.with_context(active_model='sale.order',
                             active_ids=[self.saleorder2.id],
                             active_id=self.saleorder2.id).create_invoices()
        self.assertNotEquals(
            len(self.saleorder2.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        for invoice in self.saleorder2.invoice_ids:
            invoice.date_invoice = fields.Date.today()
            invoice.signal_workflow('invoice_open')
        wizard = self.make_settle_model.create(
            {'date_to': (datetime.datetime.now() +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        wizard2 = self.make_inv_model.create({'product': 1})
        wizard2.button_create()
        settlements = self.settle_model.search([('state', '=', 'invoiced')])
        for settlement in settlements:
            self.assertNotEquals(len(settlement.invoice), 0,
                                 "Settlements need to be in Invoiced State.")

    def test_sale_commission_net_amount_payment(self):
        self.saleorder3.signal_workflow('order_confirm')
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        payment.with_context(active_model='sale.order',
                             active_ids=[self.saleorder3.id],
                             active_id=self.saleorder3.id).create_invoices()
        self.assertNotEquals(
            len(self.saleorder3.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        for invoice in self.saleorder3.invoice_ids:
            invoice.date_invoice = fields.Date.today()
            invoice.signal_workflow('invoice_open')
        wizard = self.make_settle_model.create(
            {'date_to': (datetime.datetime.now() +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertEquals(
            len(settlements), 0,
            "The Type of Commission only allows create the Settlements when"
            " the Invoices are Paid.")
        journals = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', self.saleorder3.company_id.id)
        ], limit=1)
        for invoice in self.saleorder3.invoice_ids:
            invoice.pay_and_reconcile(
                invoice.amount_total, self.ref('account.cash'),
                self.ref('account.period_8'), journals[:1].id,
                self.ref('account.cash'), self.ref('account.period_8'),
                journals[:1].id, name='test')
        self.assertNotEquals(len(self.saleorder3.invoice_ids), 0,
                             "Invoice should be created.")
        self.assertTrue(self.saleorder3.invoice_exists,
                        "Order is not invoiced.")
        self.assertTrue(self.saleorder3.invoiced, "Order is not paid.")
        for invoice in self.saleorder3.invoice_ids:
            refund_wiz = self.env['account.invoice.refund'].with_context(
                active_ids=invoice.ids, active_id=invoice.id).create({
                    'description': 'Refund test',
                    'filter_refund': 'refund',
                })
            refund_wiz.invoice_refund()

    def test_sale_commission_net_amount_invoice(self):
        self.saleorder4.signal_workflow('order_confirm')
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        payment.with_context(active_model='sale.order',
                             active_ids=[self.saleorder4.id],
                             active_id=self.saleorder4.id).create_invoices()
        self.assertNotEquals(
            len(self.saleorder4.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        for invoice in self.saleorder4.invoice_ids:
            invoice.date_invoice = fields.Date.today()
            invoice.signal_workflow('invoice_open')
        wizard = self.make_settle_model.create(
            {'date_to': (datetime.datetime.now() +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        wizard2 = self.make_inv_model.create({'product': 1})
        wizard2.button_create()
        settlements = self.settle_model.search([('state', '=', 'invoiced')])
        for settlement in settlements:
            self.assertNotEquals(len(settlement.invoice), 0,
                                 "Settlements need to be in Invoiced State.")

    def test_sale_commission_section_payment(self):
        self.saleorder5.signal_workflow('order_confirm')
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        payment.with_context(active_model='sale.order',
                             active_ids=[self.saleorder5.id],
                             active_id=self.saleorder5.id).create_invoices()
        self.assertNotEquals(
            len(self.saleorder5.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        for invoice in self.saleorder5.invoice_ids:
            invoice.date_invoice = fields.Date.today()
            invoice.signal_workflow('invoice_open')
        wizard = self.make_settle_model.create(
            {'date_to': (datetime.datetime.now() +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        settlements = self.settle_model.search([('state', '=', 'settled')])
        self.assertEquals(
            len(settlements), 0,
            "The Type of Commission only allows create the Settlements when"
            " the Invoices are Paid.")
        journals = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', self.saleorder5.company_id.id)
        ], limit=1)
        for invoice in self.saleorder5.invoice_ids:
            invoice.pay_and_reconcile(
                invoice.amount_total, self.ref('account.cash'),
                self.ref('account.period_8'), journals[:1].id,
                self.ref('account.cash'), self.ref('account.period_8'),
                journals[:1].id, name='test')
        self.assertNotEquals(len(self.saleorder5.invoice_ids), 0,
                             "Invoice should be created.")
        self.assertTrue(self.saleorder5.invoice_exists,
                        "Order is not invoiced.")
        self.assertTrue(self.saleorder5.invoiced, "Order is not paid.")

    def test_sale_commission_section_invoice(self):
        self.saleorder6.signal_workflow('order_confirm')
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        payment.with_context(active_model='sale.order',
                             active_ids=[self.saleorder6.id],
                             active_id=self.saleorder6.id).create_invoices()
        self.assertNotEquals(
            len(self.saleorder6.invoice_ids), 0,
            "Invoice should be created after make advance invoice where type"
            " is 'Invoice all the Sale Order'.")
        for invoice in self.saleorder6.invoice_ids:
            invoice.date_invoice = fields.Date.today()
            invoice.signal_workflow('invoice_open')
        wizard = self.make_settle_model.create(
            {'date_to': (datetime.datetime.now() +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        wizard2 = self.make_inv_model.create({'product': 1})
        wizard2.button_create()
        settlements = self.settle_model.search([('state', '=', 'invoiced')])
        for settlement in settlements:
            self.assertNotEquals(len(settlement.invoice), 0,
                                 "Settlements need to be in Invoiced State.")

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
                    'product_id': self.ref('product.product_product_7'),
                    'product_uom_qty': 8.0,
                })],
            })
        self.assertNotEquals(len(saleorder.mapped('order_line.agents')), 0,
                             "There should be a agent assigned to the lines.")
        self.assertTrue(
            sale_agent in saleorder.mapped('order_line.agents.agent'),
            "Sale agent in partner should be assigned in lines.")

    def test_wrong_section(self):
        with self.assertRaises(exceptions.ValidationError):
            self.commission_model.create({
                'name': 'Section commission - Invoice Based',
                'commission_type': 'section',
                'sections': [(0, 0, {
                    'amount_from': 5,
                    'amount_to': 1,
                    'percent': 20.0,
                })]
            })
