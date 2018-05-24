# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleCommissionPricelist(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleCommissionPricelist, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product 1',
            'list_price': 100,
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'Test Product 2',
            'list_price': 200,
        })
        SaleCommission = cls.env['sale.commission']
        cls.commission_agent = SaleCommission.create({
            'name': '0.5% commission',
            'fix_qty': 0.5,
        })
        cls.commission_1 = SaleCommission.create({
            'name': '1% commission',
            'fix_qty': 1.0,
        })
        cls.commission_2 = SaleCommission.create({
            'name': '2% commission',
            'fix_qty': 2.0,
        })
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Test commission pricelist',
            'item_ids': [
                (0, 0, {
                    'name': '10% discount and commission on Test product 2',
                    'applied_on': '1_product',
                    'product_id': cls.product2.id,
                    'compute_price': 'formula',
                    'base': 'list_price',
                    'price_discount': 20,
                    'commission_id': cls.commission_2.id,
                }),
                (0, 0, {
                    'name': '20%  Discount and commission',
                    'compute_price': 'percentage',
                    'base': 'list_price',
                    'percent_price': 10,
                    'applied_on': '3_global',
                    'commission_id': cls.commission_1.id,
                }),
            ]
        })
        Partner = cls.env['res.partner']
        cls.agent = Partner.create({
            'name': 'Test Agent',
            'agent': True,
            'commission': cls.commission_agent.id,
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
        cls.so_line2 = SOLine.with_context(partner_id=cls.partner.id).create({
            'order_id': cls.sale_order.id,
            'product_id': cls.product2.id,
        })
        for onchange_method in cls.so_line2._onchange_methods['product_id']:
            onchange_method(cls.so_line2)

    def test_sale_commission_pricelist(self):
        self.assertEqual(
            self.so_line1.agents[:1].commission, self.commission_1)
        self.assertEqual(
            self.so_line2.agents[:1].commission, self.commission_2)
