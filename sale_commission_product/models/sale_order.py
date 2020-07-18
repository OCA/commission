# © 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# Copyright 2020 Andrea Cometa - Apulia Software s.r.l.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()

        if self.order_id.partner_id and self.product_id:
            agent_list = []
            partner = self.order_id.partner_id

            for agent in partner.agents:
                # default commission_id for agent
                commission_id = agent.commission.id
                commission_id_product = self.env['product.product.agent']\
                    .get_commission_id_product(self.product_id.id, agent.id)
                if commission_id_product:
                    commission_id = commission_id_product
                else:
                    commission_id_category = self.env[
                        'product.category.agent'].get_commission_id_category(
                            self.product_id.categ_id, agent.id)
                    if commission_id_category:
                        commission_id = commission_id_category

                agent_list.append({'agent': agent.id,
                                   'commission': commission_id
                                   })
            if agent_list:
                self.agents = False
                self.agents = agent_list

        return res
