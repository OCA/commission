# © 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# Copyright 2020 Andrea Cometa - Apulia Software s.r.l.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    agent_ids = fields.One2many(
        string="Agents & commissions",
        oldname='agents',
        comodel_name='product.product.agent',
        inverse_name='product_id', copy=True)


class ProductProductAgent(models.Model):
    _name = 'product.product.agent'
    _description = 'Product Product Agent'

    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        ondelete="cascade")
    agent_id = fields.Many2one(
        comodel_name="res.partner", required=False, ondelete="restrict",
        oldname='agent', domain="[('agent', '=', True)]")
    commission_id = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict",
        oldname='commission')

    @api.model
    def get_commission_id_product(self, product_id, agent_id):
        commission_id = False
        commission_ids = self.search_read(
            [('product_id', '=', product_id), ('agent_id', '=', agent_id)],
            ['commission_id'])
        if not commission_ids:
            commission_ids = self.search_read(
                [('product_id', '=', product_id)], ['commission_id'])
        if commission_ids:
            commission_id = commission_ids[0]['commission_id'][0]
        return commission_id

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%s: %s" % (record.agent_id.name, record.commission_id.name)
            res.append((record.id, name))
        return res

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(product_id, agent_id)',
         'You can only add one time each agent.')
    ]


class ProductCategory(models.Model):
    _inherit = 'product.category'

    agent_ids = fields.One2many(
        string="Agents & commissions",
        oldname='agents',
        comodel_name='product.category.agent',
        inverse_name='category_id', copy=True)


class ProductCategoryAgent(models.Model):
    _name = 'product.category.agent'
    _description = 'Product Category Agent'

    category_id = fields.Many2one(
        comodel_name="product.category",
        required=True,
        ondelete="cascade",
        string="")
    agent_id = fields.Many2one(
        comodel_name="res.partner", required=True, ondelete="restrict",
        oldname='agent', domain="[('agent', '=', True)]")
    commission_id = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict",
        oldname='commission')

    @api.model
    def get_commission_id_category(self, category, agent_id):
        commission_id = False
        commission_ids = self.search_read(
            [('category_id', '=', category.id), ('agent_id', '=', agent_id)],
            ['commission_id'])
        if commission_ids:
            commission_id = commission_ids[0]['commission_id'][0]
        if not commission_id and category.parent_id:
            return self.get_commission_id_category(category.parent_id, agent_id)
        return commission_id

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%s: %s" % (record.agent_id.name, record.commission_id.name)
            res.append((record.id, name))
        return res

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(category_id, agent_id)',
         'You can only add one time each agent.')
    ]
