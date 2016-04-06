# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea Servicios Tecnologicos Sl.All Rights Reserved
#    $Javier Colmenero Fernández$ <javier@comunitea.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp import models, fields, api
from openerp import _


class ResPartnerAgent(models.Model):
    """
    Relation between partner and agents.
    """
    _name = "res.partner.agent"

    partner_id = fields.Many2one('res.partner', 'Partner', required=True,
                                 ondelete='cascade', help='', select=1)
    agent_id = fields.Many2one('res.partner', 'Agent', required=True,
                               ondelete='cascade', help='',
                               domain="[('agent', '=', True)]")
    commission_id = fields.Many2one('sale.commission', 'Applied commission',
                                    required=True, help='')

    def name_get(self, cr, uid, ids, context=None):
        """devuelve como nombre del agente del partner el nombre del agente"""
        if context is None:
            context = {}
        res = []
        for obj in self:
            res.append((obj.id, obj.agent_id.name))

        return res

    @api.onchange('agent_id')
    def onchange_agent_id(self):
        if self.agent_id:
            self.commission = self.agent_id.commission.id

    @api.onchange('commission_id', 'agent_id')
    def onchange_commission_id(self):
        res = {}
        if self.commission_id and self.commission_id.sections \
                and self.agent_id:
            if self.agent_id.commission.id != self.commission_id.id:
                res['warning'] = {}
                res['warning']['title'] = _('Fee installments!')
                res['warning']['message'] = _(
                    'A commission has been assigned by sections that '
                    'does not match that defined for the agent by '
                    'default, so that these sections shall apply '
                    'only on this bill.')
        return res
