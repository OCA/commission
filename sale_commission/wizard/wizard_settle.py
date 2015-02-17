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

from openerp import models, fields, api


class settled_wizard (models.TransientModel):
    """settled.wizard"""

    _name = "settled.wizard"

    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)

    @api.one
    def settlement_exec(self):
        pool_liq = self.env['settlement']
        vals = {
            'name': self.date_from + " // " + self.date_to,
            'date_from': self.date_from,
            'date_to': self.date_to
        }
        liq_id = pool_liq.create(vals)
        liq_id.calculate(self.env.context['active_ids'],
                         self.date_from, self.date_to)

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

    def recalculate_exec(self):
        invoice_obj = self.env['account.invoice']
        involine_obj = self.env['account.invoice.line']
        user = self.env.user
        agent_pool = self.env['invoice.line.agent']
        for data in self:
            invoice_id_lst = invoice_obj.search(
                [('state', '!=', 'draft'), ('type', '=', 'out_invoice'),
                 ('date_invoice', '>=', data.date_from),
                 ('date_invoice', '<=', data.date_to),
                 ('company_id', '=', user.company_id.id)]).ids
            invoice_lines = involine_obj.search(
                [('invoice_id', 'in', invoice_id_lst)])
            inv_line_agents = agent_pool.search(
                [('invoice_line_id', 'in', invoice_lines.ids)])
            for inv_line_agent in inv_line_agents:
                inv_line_agent.calculate_commission()
        return {}

    def action_cancel(self, connect=None):
        """Cancel Calculation"""
        return {}
