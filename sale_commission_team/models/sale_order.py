# Copyright (C) 2020, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_agent_vals_team(self, team):
        """Return a List of Dictionary Values that can be
        iterated through for Agent creation"""
        member_ids = team.member_ids
        partner_ids = [member_id.partner_id for member_id
                       in member_ids if member_id.partner_id.agent]
        agent_vals = []
        for partner_id in partner_ids:
            agent = {'agent': partner_id.id,
                     'commission': partner_id.commission.id}
            agent_vals.append(agent)
        return agent_vals

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('user_id', False) and self.env.user.\
                company_id.sale_commission_automation_option == 'user':
            user_id = self.user_id
            for line_id in self.order_line:
                line_id.agents = [(5, 0, line_id.agents.ids)]
                agent_val = self._prepare_agent_vals_user(user_id)
                agent_val.update({'object_id': line_id.id})
                line_id.agents = [(4, self.env['sale.order.line.agent'].
                                   create(agent_val).id)]
        elif vals.get('team_id', False) and self.env.user.\
                company_id.sale_commission_automation_option == 'team':
            agent_vals = self._prepare_agent_vals_team(self.team_id)
            for line_id in self.order_line:
                line_id.agents = [(5, 0, line_id.agents.ids)]
                for val in agent_vals:
                    val.update({'object_id': line_id.id})
                agent_ids = [self.env['sale.order.line.agent'].
                             create(val).id for val in agent_vals]
            line_id.agents = [(6, 0, agent_ids)]
        return res

    def _prepare_agent_vals_user(self, user_id):
        return {'agent': user_id.partner_id.id,
                'commission': user_id.partner_id.commission.id}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def create(self, vals):
        line_id = super().create(vals)
        if line_id.order_id.team_id and self.env.user.\
                company_id.sale_commission_automation_option == 'team':
            agent_vals = line_id.order_id.\
                _prepare_agent_vals_team(line_id.order_id.team_id)
            for agent in line_id.agents:
                    line_id.agents = [(2, agent.id)]
            for val in agent_vals:
                val.update({'object_id': line_id.id})
                self.env['sale.order.line.agent'].create(val)
        elif line_id.order_id.user_id and self.env.user.\
                company_id.sale_commission_automation_option == 'user':
            agent_vals = line_id.order_id.\
                _prepare_agent_vals_user(line_id.order_id.user_id)
            agent_vals.update({'object_id': line_id.id})
            for agent in line_id.agents:
                    line_id.agents = [(2, agent.id)]
            self.env['sale.order.line.agent'].create(agent_vals)
        return line_id
