# Copyright 2020 Andrea Cometa - Apulia Software s.r.l.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase


class TestCommissionProduct(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommissionProduct, cls).setUpClass()

        SaleCommission = cls.env['sale.commission']
        cls.commission_agent = SaleCommission.create({
            'name': '5% commission',
            'fix_qty': 5,
        })
        cls.commission_1 = SaleCommission.create({
            'name': '10% commission',
            'fix_qty': 10,
        })
        cls.commission_2 = SaleCommission.create({
            'name': '20% commission',
            'fix_qty': 20,
        })

        Partner = cls.env['res.partner']
        cls.agent = Partner.create({
            'name': 'Test Agent',
            'agent': True,
            'commission': cls.commission_agent.id,
        })
        cls.partner = Partner.create({
            'name': 'Test Partner',
            'customer': True,
            'supplier': False,
            'agents': [(6, 0, cls.agent.ids)],
        })

        Product = cls.env['product.product']
        cls.product = Product.create({
            'name': 'Test Product 1',
            'list_price': 100,
        })
        cls.product2 = Product.create({
            'name': 'Test Product 2',
            'list_price': 200,
        })

        ProductAgent = cls.env['product.product.agent']
        cls.productagent = ProductAgent.create({
            'product_id': cls.product.id,
            'commission': cls.commission_1.id,
            'agent': cls.agent.id,
        })
        cls.productagent2 = ProductAgent.create({
            'product_id': cls.product2.id,
            'commission': cls.commission_2.id,
            'agent': False,
        })

        ProductCategory = cls.env['product.category']
        cls.category = ProductCategory.create({
            'name': 'Test Product Category',
        })
        cls.product3 = Product.create({
            'name': 'Test Product 3',
            'list_price': 200,
            'categ_id': cls.category.id,
        })

        ProductCategoryAgent = cls.env['product.category.agent']
        cls.product_cat_agent = ProductCategoryAgent.create({
            'category_id': cls.category.id,
            'commission': cls.commission_2.id,
            'agent': cls.agent.id,
        })

        SaleOrder = cls.env['sale.order']
        cls.sale_order = SaleOrder.create({
            'partner_id': cls.partner.id,
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
        cls.so_line3 = SOLine.with_context(partner_id=cls.partner.id).create({
            'order_id': cls.sale_order.id,
            'product_id': cls.product3.id,
        })
        for onchange_method in cls.so_line3._onchange_methods['product_id']:
            onchange_method(cls.so_line3)

    def test_commission_product(self):
        self.assertEqual(
            self.so_line1.agents[:1].commission, self.commission_1)
        self.assertEqual(
            self.so_line2.agents[:1].commission, self.commission_2)
        self.assertEqual(
            self.so_line3.agents[:1].commission, self.commission_2)
