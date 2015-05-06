# -*- coding: utf-8 -*-
##############################################################################
#
#    KMEE, KM Enterprising Engineering
#    Copyright(C) 2015 - Daniel Sadamo <daniel.sadamo@kmee.com.br>
#
#    This program is free software: you can redistribute it and    /or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv


class hr_payslip(osv.osv):

    _inherit = 'hr.payslip'

    def onchange_input_line_ids(self, cr, uid, ids, input_line_ids,
                                date_from, date_to,
                                employee_id=False, context=None):
        if context is None:
            context = {}

        res = {'value': {}}
        if not employee_id:
            return res
        # Get the total commission for the date interval
        settlement_obj = self.pool.get('settlement')
        settlements_ids = settlement_obj.search(
            cr, uid,
            [('date_from', '>=', date_from), ('date_to', '<=', date_to)],
            context=context)
        commission_amount = 0.0
        settlements = settlement_obj.browse(cr, uid, settlements_ids, context)
        for settlement in settlements:
                for agent in settlement.settlement_agent_id:
                    if agent.agent_id.employee_id.id == employee_id:
                        commission_amount += agent.total
        # Insert the commission value in the input list
        for input_line in input_line_ids:
            if input_line[2]:
                if 'code' in input_line[2] and\
                        (input_line[2]['code'] == 'COM'):
                    input_line[2]['amount'] = commission_amount

        res['value'].update({
            'input_line_ids': input_line_ids,
        })

        return res
