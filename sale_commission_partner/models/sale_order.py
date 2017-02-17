# -*- coding: utf-8 -*-
# Copyright 2016 Apulia Software srl (<http://www.apuliasoftware.it>)
# Andrea Cometa <a.cometa@apuliasoftware.it>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_agents(self):
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for agent in partner.agents_partner:
                vals = {
                    'agent': agent.agent_id.id,
                    'commission': agent.commission.id,
                }
                vals['display_name'] = self.env['sale.order.line.agent']\
                    .new(vals).display_name
                agents.append(vals)
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name='sale.order.line.agent', inverse_name='sale_line',
        copy=True, readonly=True, default=_default_agents)


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")

    @api.onchange('agent')
    def onchange_agent(self):
        if self.agent in self.sale_line.order_id.partner_id.agent_partner:
            for a in self.sale_line.order_id.partner_id.agent_partner:
                if a == self.agent:
                    print a, a.commission
                    self.commission = a.commission
