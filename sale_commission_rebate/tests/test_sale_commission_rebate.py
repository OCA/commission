# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestSaleCommissionRebate(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleCommissionRebate, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product 1',
            'list_price': 100,
        })
        SaleCommission = cls.env['sale.commission']
        cls.commission_1 = SaleCommission.create({
            'name': '1% commission',
            'fix_qty': 1.0,
        })

        Partner = cls.env['res.partner']
        cls.agent = Partner.create({
            'name': 'Test Agent',
            'agent': True,
            'commission': cls.commission_1.id,
        })
        env['product.supplierinfo'].create({
            'name': cls.agent.id,
            'product_id': cls.product.id,
            'product_code': '00001',
            'price': 100.0,
            'rebate_price': 80.0,
        })
        cls.partner = Partner.create({
            'name': 'Partner test',
            'customer': True,
            'supplier': False,
            'agents': [(6, 0, cls.agent.ids)],
        })
        SaleOrder = cls.env['sale.order']
        cls.sale_order = SaleOrder.create({
            'partner_id': cls.partner.id,
            'pricelist_id': cls.pricelist.id,
        })
        SOLine = cls.env['sale.order.line']
        cls.so_line1 = SOLine.with_context(partner_id=cls.partner.id).create({
            'order_id': cls.sale_order.id,
            'product_id': cls.product.id,
        })
        for onchange_method in cls.so_line1._onchange_methods['product_id']:
            onchange_method(cls.so_line1)

    def test_sale_commission_rebate(self):
        self.assertEquals(
            self.so_line1.agents[:1].commission, self.commission_1)
