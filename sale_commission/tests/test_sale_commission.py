# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.sale_commission.models.settlement import Settlement
from odoo import fields
from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError, ValidationError
import dateutil.relativedelta
from unittest.mock import patch


class TestSaleCommission(SavepointCase):
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
                'product_uom': self.ref('product.product_uom_unit'),
                'price_unit': self.product.list_price,
                'agents': [(0, 0, {
                    'agent': agent.id,
                    'commission': commission.id
                })]
            })]
        })

    def test_sale_commission_gross_amount_payment(self):
        self.check_full(
            self.env.ref('sale_commission.res_partner_pritesh_sale_agent'),
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

    def test_sale_commission_gross_amount_invoice(self):
        sale_order = self._create_sale_order(
            self.agent_quaterly,
            self.env.ref('sale_commission.demo_commission')
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
            self.env.ref('sale_commission.res_partner_pritesh_sale_agent'),
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
            self.env.ref('sale_commission.res_partner_pritesh_sale_agent'),
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
        sale_agent = self.env.ref(
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

    def test_sale_order_onchange_commission_status(self):
        # Make sure user is in English
        self.env.user.lang = 'en_US'
        sale_order = self._create_sale_order(
            self.env.ref('sale_commission.res_partner_pritesh_sale_agent'),
            self.commission_section_invoice,
        )
        self.assertIn("1", sale_order.order_line[0].commission_status)
        self.assertNotIn("agents", sale_order.order_line[0].commission_status)
        sale_order.mapped('order_line.agents').unlink()
        self.assertIn("No", sale_order.order_line[0].commission_status)
        sale_order.order_line[0].agents = [
            (0, 0, {
                'agent': self.env.ref(
                    'sale_commission.res_partner_pritesh_sale_agent'
                ).id,
                'commission': self.env.ref(
                    'sale_commission.demo_commission'
                ).id,
            }),
            (0, 0, {
                'agent': self.env.ref(
                    'sale_commission.res_partner_eiffel_sale_agent'
                ).id,
                'commission': self.env.ref(
                    'sale_commission.demo_commission'
                ).id,
            }),
        ]
        self.assertIn("2", sale_order.order_line[0].commission_status)
        self.assertIn("agents", sale_order.order_line[0].commission_status)
        sale_order.order_line[0].commission_free = True
        self.assertIn("free", sale_order.order_line[0].commission_status)

    def test_invoice(self):
        self.partner.agent = False
        self.partner.agents = self.agent_semi
        partner = self.env.ref('base.res_partner_12')
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

    def test_join_settlements(self):
        self.product.write({'list_price': 1000})
        agent = self.agent_monthly
        commission = self.commission_net_invoice
        period = 1
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
        settlements = self.settle_model.search([('agent', '=', agent.id)])
        self.assertEqual(1, len(settlements))
        wizard2 = self.make_inv_model.create({
            'product': 1,
            'journal': self.journal.id
        })
        wizard2.button_create()
        agent_invoice = settlements.invoice
        for invoice in sale_order.invoice_ids:
            refund = invoice.refund()
            refund.action_invoice_open()
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=period))})
        wizard.action_settle()
        settlements = self.settle_model.search([('agent', '=', agent.id)])
        self.assertEqual(2, len(settlements))
        self.assertTrue(settlements.filtered(lambda r: r.total < 0))
        with patch.object(
            Settlement,
            'create_invoice_header', return_value=agent_invoice
        ):
            wizard2 = self.make_inv_model.create({
                'product': 1,
                'journal': self.journal.id
            })
            wizard2.button_create()

    def test_negative_settlements(self):
        self.product.write({'list_price': 1000})
        agent = self.agent_monthly
        commission = self.commission_net_invoice
        period = 1
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
        settlements = self.settle_model.search([('agent', '=', agent.id)])
        self.assertEqual(1, len(settlements))
        wizard2 = self.make_inv_model.create({
            'product': 1,
            'journal': self.journal.id
        })
        wizard2.button_create()
        for invoice in sale_order.invoice_ids:
            refund = invoice.refund()
            refund.action_invoice_open()
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=period))})
        wizard.action_settle()
        settlements = self.settle_model.search([('agent', '=', agent.id)])
        self.assertEqual(2, len(settlements))

        self.assertTrue(settlements.filtered(lambda r: r.total < 0))
        with self.assertRaises(UserError):
            wizard2 = self.make_inv_model.create({
                'product': 1,
                'journal': self.journal.id
            })
            wizard2.button_create()

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

    def test_res_partner_agent_propagation(self):
        partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'agents': [
                (4, self.agent_monthly.id), (4, self.agent_quaterly.id),
            ],
        })
        # Onchange
        child = self.env['res.partner'].new({
            'name': 'Test child',
            'parent_id': partner.id,
        })
        child.onchange_parent_id()
        self.assertEqual(child.agents, partner.agents)
        # Create
        child = self.env['res.partner'].create({
            'name': 'Test child',
            'parent_id': partner.id,
        })
        self.assertEqual(child.agents, partner.agents)
        # Write
        partner.agents = [(4, self.agent_monthly.id)]
        self.assertEqual(child.agents, partner.agents)
        # Default
        child = self.env['res.partner'].with_context(
            default_parent_id=partner.id,
        ).create({
            'name': 'Test child',
        })
        self.assertEqual(child.agents, partner.agents)
