from odoo import models, api, _
from datetime import timedelta


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    @api.multi
    def action_settle(self):
        agent_line_obj = self.env['sale.order.line.agent']
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        if not self.agents:
            self.agents = self.env['res.partner'].search(
                [('agent', '=', True)])
        order_based_agents = self.agents.filtered(
            lambda a: a.commission.invoice_state == "confirmed_orders")
        invoice_based_agents = self.agents.filtered(
            lambda a: a.commission.invoice_state != "confirmed_orders")
        self.agents = invoice_based_agents

        res = super(SaleCommissionMakeSettle, self).action_settle()
        if "domain" in res:
            settlement_ids = res["domain"][0][2]
        else:
            settlement_ids = []

        date_to = self.date_to
        for agent in order_based_agents:
            date_to_agent = self._get_period_start(agent, date_to)
            agent_lines = agent_line_obj.search(
                [('order_date', '<', date_to_agent),
                 ('order_state', '=', "sale"),
                 ('agent', '=', agent.id),
                 ('settled', '=', False)], order='order_date')
            for agent_line in agent_lines:
                company = agent_line.company_id
                if not agent_line.order_date:
                    continue
                sett_from = self._get_period_start(
                    agent, agent_line.order_date)
                sett_to = self._get_next_period_date(
                    agent, sett_from,
                ) - timedelta(days=1)
                settlement = self._get_settlement(
                    agent, company, sett_from, sett_to)
                if not settlement:
                    settlement = settlement_obj.create(
                        self._prepare_settlement_vals(
                            agent, company, sett_from, sett_to))
                settlement_ids.append(settlement.id)
                settlement_line_obj.create({
                    'settlement': settlement.id,
                    'agent_sale_line': [(6, 0, [agent_line.id])],
                })

        if settlement_ids:
            return {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }
        else:
            return {'type': 'ir.actions.act_window_close'}
