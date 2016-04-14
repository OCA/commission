# -*- coding: utf-8 -*-
# © 2015 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# © 2015 Javier Colmenero Fernández (<javier@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _default_agents(self):
        """
        Overwrites the original default_get in order to get agents and
        commissions from the new partner field commission_ids
        """
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for com_obj in partner.commission_ids:
                vals = {
                    'agent': com_obj.agent_id.id,
                    'commission': com_obj.commission_id.id
                }
                vals['display_name'] = self.env['sale.order.line.agent']\
                    .new(vals).display_name
                agents.append(vals)
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(
        comodel_name="account.invoice.line.agent",
        inverse_name="invoice_line", string="Agents & commissions",
        help="Agents/Commissions related to the invoice line.",
        default=_default_agents, copy=True)


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    @api.onchange('agent')
    def onchange_agent(self):
        res_commission = super(AccountInvoiceLineAgent, self).onchange_agent()
        if self.env.context.get('partner_id'):
            domain = [
                ('partner_id', '=', self.env.context['partner_id']),
                ('agent_id', '=', self.agent.id),
            ]
            rel_objs = self.env['res.partner.agent'].search(domain, limit=1)
            if rel_objs:
                res_commission = rel_objs.commission_id.id
        self.commission = res_commission
