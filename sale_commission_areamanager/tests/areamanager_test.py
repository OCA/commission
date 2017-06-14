# -*- coding: utf-8 -*-

import openerp.tests.common as common


class TestAreaManagerCommission(common.TransactionCase):

    def setUp(self):
        super(TestAreaManagerCommission, self).setUp()
        self.commission_model = self.env['sale.commission']
        self.res_partner_model = self.env['res.partner']
        self.areamanager = self.res_partner_model.create({
            'name': 'Test AreaManager',
            'agent': True,
            'settlement': 'quaterly',
            'lang': 'en_US',
            'area_manager': True,
        })
        self.commission_net_invoice = self.commission_model.create({
            'name': '10% fixed commission (Net amount) - Invoice Based',
            'fix_qty': 10.0,
            'amount_base_type': 'net_amount',
        })
        self.commission_areamanger = self.commission_model.create({
            'name': '5% fixed commission (Net amount) - Invoice Based',
            'fix_qty': 5.0,
            'amount_base_type': 'net_amount',
        })
        self.agent = self.res_partner_model.create({
            'name': 'Test Agent',
            'agent': True,
            'settlement': 'quaterly',
            'lang': 'en_US',
            'area_manager': False,
            'area_manager_id': self.areamanager.id,
            'commission_for_areamanager': self.commission_areamanger.id,
        })
        self.partner = self.browse_ref('base.res_partner_2')
        self.partner.write({'supplier': False, 'agent': self.agent})
        self.sale_order_model = self.env['sale.order']
        self.product = self.browse_ref('product.product_product_5')
        self.product.write({
            'invoice_policy': 'order',
        })
        self.saleorder1 = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 8.0,
                'product_uom': self.ref('product.product_uom_unit'),
                'price_unit': self.product.lst_price,
                'agents': [(0, 0, {
                    'agent': self.agent.id,
                    'commission': self.commission_net_invoice
                })]
            })]
        })

    def test_areamanager_onchange_and_commission(self):
        sale_agent = [self.agent.id, self.areamanager.id]
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
        self.assertNotEquals(len(saleorder.mapped('order_line.agents')), 0,
                             "There should be a agent assigned to the lines.")
        self.assertNotEquals(len(saleorder.mapped('order_line.agents')), 1,
                             "There should be a areamanager "
                             "assigned to the lines.")
        self.assertTrue(
            sale_agent in saleorder.mapped('order_line.agents.agent'),
            "Sale agent in partner should be assigned in lines.")
