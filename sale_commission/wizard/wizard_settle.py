# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#    Copyright (C) 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from ..models.sale_commission import (
    PERIOD_MONTH,
    PERIOD_QUARTER,
    PERIOD_SEMI,
    PERIOD_YEAR,
)


class SaleCommissionMakeSettle(models.TransientModel):
    _name = "sale.commission.make.settle"

    date_to = fields.Date('Up to', required=True, default=fields.Date.today())
    agents = fields.Many2many(comodel_name='res.partner',
                              domain="[('agent', '=', True)]")

    @classmethod
    def _get_period_start(cls, period, date_to):
        if isinstance(date_to, basestring):
            date_to = fields.Date.from_string(date_to)
        if period == PERIOD_MONTH:
            return date(month=date_to.month, year=date_to.year, day=1)
        elif period == PERIOD_QUARTER:
            # Get first month of the date quarter
            month = ((date_to.month - 1) // 3) * 3 + 1
            return date(month=month, year=date_to.year, day=1)
        elif period == PERIOD_SEMI:
            if date_to.month > 6:
                return date(month=7, year=date_to.year, day=1)
            else:
                return date(month=1, year=date_to.year, day=1)
        elif period == PERIOD_YEAR:
            return date(month=1, year=date_to.year, day=1)
        else:
            raise exceptions.Warning(_("Settlement period not valid."))

    @classmethod
    def _get_period_end(cls, period, date):
        start = cls._get_period_start(period, date)
        end = cls._get_next_period_date(period, start) - relativedelta(days=1)
        return end

    @classmethod
    def _get_next_period_date(cls, period, current_date):
        if isinstance(current_date, basestring):
            current_date = fields.Date.from_string(current_date)
        if period == PERIOD_MONTH:
            return current_date + relativedelta(months=1)
        elif period == PERIOD_QUARTER:
            return current_date + relativedelta(months=3)
        elif period == PERIOD_SEMI:
            return current_date + relativedelta(months=6)
        elif period == PERIOD_YEAR:
            return current_date + relativedelta(years=1)
        else:
            raise exceptions.Warning(_("Settlement period not valid."))

    @api.multi
    def action_settle(self):
        self.ensure_one()
        commission_line_obj = self.env['account.invoice.line.commission']
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        if not self.agents:
            self.agents = self.env['res.partner'].search(
                [('agent', '=', True)])
        date_to = fields.Date.from_string(self.date_to)
        for agent in self.agents:
            agent_period = agent.settlement
            date_to_agent = self._get_period_start(agent_period, date_to)
            # Get non settled invoices
            commission_lines = commission_line_obj.search(
                [('invoice_date', '<', date_to_agent),
                 ('agent', '=', agent.id),
                 ('settled', '=', False)], order='invoice_date')

            if not commission_lines:
                # Nothing to settle, carry on
                continue
            # Group lines according to period types
            periods = {}
            for line in commission_lines:
                periods.setdefault(line.commission.period, []).append(line)

            # Go through each period type, creating settlements as required
            for period, lines in periods.items():
                sett_to = date(year=1900, month=1, day=1)
                sett_to_str = fields.Date.to_string(sett_to)
                for line in lines:
                    if line.invoice_date > sett_to_str:
                        sett_from = self._get_period_start(period,
                                                           line.invoice_date)
                        sett_to = (
                            self._get_next_period_date(period, sett_from) -
                            timedelta(days=1))
                        sett_to_str = fields.Date.to_string(sett_to)

                        # Do not allow settling unfinished periods
                        if sett_to >= date_to:
                            break

                        sett_from = fields.Date.to_string(sett_from)
                        settlement = settlement_obj.create(
                            {'agent': agent.id,
                             'date_from': sett_from,
                             'date_to': sett_to_str})

                    settlement_line_obj.create(
                        {'settlement': settlement.id,
                         'agent_line': [(6, 0, [line.id])]})

        return True
