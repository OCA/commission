# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_agents(self):
        super(SaleOrderLine, self)._default_agents()
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for agent in partner.agents:
                commission = agent.plan.get_product_commission()
                if commission:
                    vals = {
                        'agent': agent.id,
                        'commission': commission.id,
                    }
                    vals['display_name'] = self.env['sale.order.line.agent']\
                        .new(vals).display_name
                    agents.append(vals)
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(default=_default_agents)
