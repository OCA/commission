# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 Asr Oss (http://www.asr-oss.com)
#                       Alejandro Sanchez Ramirez <alejandro@asr-oss.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name='product.template.agent', inverse_name='product_id',
        copy=True, readonly=True)


class ProductTemplateAgent(models.Model):
    _name = 'product.template.agent'

    @api.multi
    def get_commission_id_product(self, product, agent):
        commission_id = False
        # commission_id for all agent
        for commission_all_agent in self.search(
                [('product_id', '=', product), ('agent', '=', False)]):
                    commission_id = commission_all_agent.commission.id
        # commission_id for agent
        for product_tmp_agent_id in self.search(
                        [('product_id', '=', product),
                         ('agent', '=', agent.id)]):
                    commission_id = product_tmp_agent_id.commission.id
        return commission_id

    product_id = fields.Many2one(
        comodel_name="product.template",
        required=True,
        ondelete="cascade",
        string="")
    agent = fields.Many2one(
        comodel_name="res.partner", required=False, ondelete="restrict",
        domain="[('agent', '=', True')]")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(product_id, agent)',
         'You can only add one time each agent.')
    ]
