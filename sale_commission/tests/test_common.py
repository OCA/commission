# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields
from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError, ValidationError
import dateutil.relativedelta


class TestCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env['sale.commission']
        cls.commission_net_paid = cls.commission_model.create({
            'name': '20% fixed commission (Net amount) - Payment Based',
            'fix_qty': 20.0,
            'invoice_state': 'paid',
            'amount_base_type': 'net_amount',
        })
        cls.commission_net_invoice = cls.commission_model.create({
            'name': '10% fixed commission (Net amount) - Invoice Based',
            'fix_qty': 10.0,
            'amount_base_type': 'net_amount',
        })
        cls.commission_section_paid = cls.commission_model.create({
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
        cls.commission_section_invoice = cls.commission_model.create({
            'name': 'Section commission - Invoice Based',
            'commission_type': 'section',
            'sections': [(0, 0, {
                'amount_from': 15000.0,
                'amount_to': 16000.0,
                'percent': 20.0,
            })]
        })
        cls.res_partner_model = cls.env['res.partner']
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.partner.write({'supplier': False, 'agent': False})
        cls.sale_order_model = cls.env['sale.order']
        cls.advance_inv_model = cls.env['sale.advance.payment.inv']
        cls.settle_model = cls.env['sale.commission.settlement']
        cls.make_settle_model = cls.env['sale.commission.make.settle']
        cls.make_inv_model = cls.env['sale.commission.make.invoice']
        cls.product = cls.env.ref('product.product_product_5')
        cls.product.write({
            'invoice_policy': 'order',
        })
        cls.journal = cls.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1
        )
        cls.agent_monthly = cls.res_partner_model.create({
            'name': 'Test Agent - Monthly',
            'agent': True,
            'settlement': 'monthly',
            'lang': 'en_US',
        })
        cls.agent_quaterly = cls.res_partner_model.create({
            'name': 'Test Agent - Quaterly',
            'agent': True,
            'settlement': 'quaterly',
            'lang': 'en_US',
        })
        cls.agent_semi = cls.res_partner_model.create({
            'name': 'Test Agent - Semi-annual',
            'agent': True,
            'settlement': 'semi',
            'lang': 'en_US',
        })
        cls.agent_annual = cls.res_partner_model.create({
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
                'product_uom': self.ref('uom.product_uom_unit'),
                'price_unit': self.product.lst_price,
                'agents': [(0, 0, {
                    'agent': agent.id,
                    'commission': commission.id
                })]
            })]
        })

    def check_full(self, agent, commission, period):
        sale_order = self._create_sale_order(
            agent,
            commission
        )
        sale_order.action_confirm()
        self.assertEqual(sale_order.agent_ids.ids, agent.ids)
        self.assertEqual(
            self.sale_order_model.search(
                [('agent_ids', '=', agent.name)]).ids,
            sale_order.ids)
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
            self.assertEqual(invoice.agent_ids.ids, agent.ids)
            self.assertEqual(
                self.env["account.invoice"].search(
                    [('agent_ids', '=', agent.name)]).ids,
                invoice.ids)
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
        self.assertTrue(settlements)
        inv_line = sale_order.mapped('invoice_ids.invoice_line_ids')[0]
        self.assertTrue(inv_line.any_settled)
        with self.assertRaises(ValidationError):
            inv_line.agents.amount = 5
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
