# -*- coding: utf-8 -*-
# © 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name='product.product.agent', inverse_name='product_id',
        copy=True, readonly=True)


class ProductProductAgent(models.Model):
    _name = 'product.product.agent'

    @api.multi
    def get_commission_id_product(self, product, agent):
        commission_id = False
        # commission_id for all agent
        for commission_all_agent in self.search(
                [('product_id', '=', product), ('agent', '=', False)]):
                    commission_id = commission_all_agent.commission.id
        # commission_id for agent
        for product_agent_id in self.search(
                [('product_id', '=', product), ('agent', '=', agent.id)]):
                    commission_id = product_agent_id.commission.id
        return commission_id

    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        ondelete="cascade",
        string="")
    agent = fields.Many2one(
        comodel_name="res.partner", required=False, ondelete="restrict",
        domain="[('agent', '=', True')]")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%s: %s" % (record.agent.name, record.commission.name)
            res.append((record.id, name))
        return res

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(product_id, agent)',
         'You can only add one time each agent.')
    ]
