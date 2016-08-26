# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class SaleCommissionMakeSettle(models.TransientModel):
    _name = "sale.commission.make.settle"

    date_to = fields.Date('Up to', required=True, default=fields.Date.today())
    agents = fields.Many2many(comodel_name='res.partner',
                              domain="[('agent', '=', True)]")

    def _get_period_start(self, agent, date_to):
        if isinstance(date_to, basestring):
            date_to = fields.Date.from_string(date_to)
        if agent.settlement == 'monthly':
            return date(month=date_to.month, year=date_to.year, day=1)
        elif agent.settlement == 'quaterly':
            # Get first month of the date quarter
            month = ((date_to.month - 1) // 3 + 1) * 3
            return date(month=month, year=date_to.year, day=1)
        elif agent.settlement == 'semi':
            if date_to.month > 6:
                return date(month=7, year=date_to.year, day=1)
            else:
                return date(month=1, year=date_to.year, day=1)
        elif agent.settlement == 'annual':
            return date(month=1, year=date_to.year, day=1)
        else:
            raise exceptions.Warning(_("Settlement period not valid."))

    def _get_next_period_date(self, agent, current_date):
        if isinstance(current_date, basestring):
            current_date = fields.Date.from_string(current_date)
        if agent.settlement == 'monthly':
            return current_date + relativedelta(months=1)
        elif agent.settlement == 'quaterly':
            return current_date + relativedelta(months=3)
        elif agent.settlement == 'semi':
            return current_date + relativedelta(months=6)
        elif agent.settlement == 'annual':
            return current_date + relativedelta(years=1)
        else:
            raise exceptions.Warning(_("Settlement period not valid."))

    @api.multi
    def action_settle(self):
        self.ensure_one()
        agent_line_obj = self.env['account.invoice.line.agent']
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        settlement_ids = []
        if not self.agents:
            self.agents = self.env['res.partner'].search(
                [('agent', '=', True)])
        date_to = fields.Date.from_string(self.date_to)
        for agent in self.agents:
            date_to_agent = self._get_period_start(agent, date_to)
            # Get non settled invoices
            agent_lines = agent_line_obj.search(
                [('invoice_date', '<', date_to_agent),
                 ('agent', '=', agent.id),
                 ('settled', '=', False),
                 ('invoice.type', 'in', ('out_invoice', 'out_refund'))],
                order='invoice_date')
            for company in agent_lines.mapped('invoice_line.company_id'):
                for agent_lines_company in agent_lines.filtered(
                        lambda r: r.invoice_line.company_id == company):
                    if agent_lines_company:
                        pos = 0
                        sett_to = fields.Date.to_string(date(year=1900,
                                                             month=1,
                                                             day=1))
                        while pos < len(agent_lines_company):
                            if (agent.commission.invoice_state == 'paid' and
                                    agent_lines_company[pos].invoice.state !=
                                    'paid'):
                                pos += 1
                                continue
                            if agent_lines_company[pos].invoice_date > sett_to:
                                sett_from = self._get_period_start(
                                    agent,
                                    agent_lines_company[pos].invoice_date)
                                sett_to = fields.Date.to_string(
                                    self._get_next_period_date(agent,
                                                               sett_from) -
                                    timedelta(days=1))
                                sett_from = fields.Date.to_string(sett_from)
                                settlement = settlement_obj.create(
                                    {'agent': agent.id,
                                     'date_from': sett_from,
                                     'date_to': sett_to,
                                     'company_id': company.id})
                                settlement_ids.append(settlement.id)
                            settlement_line_obj.create(
                                {'settlement': settlement.id,
                                 'agent_line': [(6, 0,
                                                 [agent_lines_company[pos].id])
                                                ]})
                            pos += 1

        # go to results
        if len(settlement_ids):
            return {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }

        else:
            return {'type': 'ir.actions.act_window_close'}
