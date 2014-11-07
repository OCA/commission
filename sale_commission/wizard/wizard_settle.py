# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#    All Rights Reserved
#    $Id$
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
from openerp import models, fields


class settled_wizard (models.TransientModel):
    """settled.wizard"""

    _name = "settled.wizard"

    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)

    def settlement_exec(self, cr, uid, ids, context=None):
        """se ejecuta correctamente desde dos."""
        if context is None:
            context = {}
        pool_liq = self.pool.get('settlement')
        for o in self.browse(cr, uid, ids, context=context):
            vals = {
                'name': o.date_from + " // " + o.date_to,
                'date_from': o.date_from,
                'date_to': o.date_to
            }
            liq_id = pool_liq.create(cr, uid, vals, context=context)
            pool_liq.calculate(
                cr, uid, liq_id,
                context['active_ids'],
                o.date_from,
                o.date_to,
                context=context
            )

        return {
            'type': 'ir.actions.act_window_close',
        }

    def action_cancel(self, cr, uid, ids, connect=None, context=None):
        """Cancel Liquidation"""
        return {
            'type': 'ir.actions.act_window_close',
        }


class recalculate_commission_wizard(models.TransientModel):
    """settled.wizard"""

    _name = "recalculate.commission.wizard"

    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)

    def recalculate_exec(self, cr, uid, ids, context=None):
        """se ejecuta correctamente desde dos."""
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        agent_pool = self.pool.get('invoice.line.agent')
        for o in self.browse(cr, uid, ids, context=context):
            sql = 'SELECT  invoice_line_agent.id FROM account_invoice_line ' \
                  'INNER JOIN invoice_line_agent ON invoice_line_agent.invoice_line_id=account_invoice_line.id ' \
                  'INNER JOIN account_invoice ON account_invoice_line.invoice_id = account_invoice.id ' \
                  'WHERE invoice_line_agent.agent_id in (' + ",".join(map(str, context['active_ids'])) + ') ' \
                  'AND invoice_line_agent.settled=False ' \
                  'AND account_invoice.state<>\'draft\' AND account_invoice.type=\'out_invoice\'' \
                  'AND account_invoice.date_invoice >= \'' + o.date_from + '\' ' \
                  'AND account_invoice.date_invoice <= \'' + o.date_to + '\' ' \
                  'AND account_invoice.company_id = ' + str(user.company_id.id)
            cr.execute(sql)
            res = cr.fetchall()
            inv_line_agent_ids = [x[0] for x in res]
            agent_pool.calculate_commission(
                cr, uid, inv_line_agent_ids, context=context
            )
        return {
            'type': 'ir.actions.act_window_close',
        }

    def action_cancel(self, cr, uid, ids, connect=None, context=None):
        """Cancel Calculation"""
        return {
            'type': 'ir.actions.act_window_close',
        }
