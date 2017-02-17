# -*- coding: utf-8 -*-
# Copyright 2016 Apulia Software srl (<http://www.apuliasoftware.it>)
# Andrea Cometa <a.cometa@apuliasoftware.it>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

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
                print agent.commission
                vals['display_name'] = self.env['account.invoice.line.agent']\
                    .new(vals).display_name
                agents.append(vals)
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(
        comodel_name="account.invoice.line.agent",
        inverse_name="invoice_line", string="Agents & commissions",
        help="Agents/Commissions related to the invoice line.",
        default=_default_agents, copy=True)
