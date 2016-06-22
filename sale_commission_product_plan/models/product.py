# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api


class ProductProductAgent(models.Model):
    _inherit = 'product.product.agent'

    @api.multi
    def get_commission_id_product(self, product, agent):
        super(ProductProductAgent, self).get_commission_id_product(product,
                                                                   agent)
        return agent.plan.get_product_commission(product).id
