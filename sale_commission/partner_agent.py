# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
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

"""objeto de comportamiento many2many que relaciona agentes o comerciales con partners"""

from osv import fields, osv
from tools.translate import _

class res_partner_agent(osv.osv):
    "objeto de comportamiento many2many que relaciona agentes o comerciales con partners"
    _name = "res.partner.agent"

    def name_get(self, cr, uid, ids, context=None):
        """devuelve como nombre del agente del partner el nombre del agente"""
        if context is None: context = {}
        res = []
        for obj in self.browse(cr, uid, ids):
            res.append((obj.id, obj.agent_id.name))

        return res

    def _get_partner_agents_to_update_from_sale_agents(self, cr, uid, ids, context=None):
        """devuelve los ids de partner agents a actualizar desde el lanzamiento de un evento de actualización en agentes de ventas"""
        if context is None: context = {}
        result = []
        for agent_obj_id in self.browse(cr, uid, ids):
            partner_agents_ids = self.pool.get('res.partner.agent').search(cr, uid, [('agent_id', '=', agent_obj_id.id)])
            result.extend(partner_agents_ids)
        return result

    _columns = {
        'partner_id':fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade', help='', select=1),
        'agent_id':fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id':fields.many2one('commission', 'Applied commission', required=True, ondelete='cascade', help=''),
        'type': fields.related('agent_id', 'type', type="selection", selection=[('asesor', 'Adviser'), ('comercial', 'Commercial')], readonly=True,
                    store={'sale.agent': (_get_partner_agents_to_update_from_sale_agents, ['type'], 10),
                            'res.partner.agent': (lambda self, cr, uid, ids, c={}: ids, None, 20)})
    }
    
    def onchange_agent_id(self, cr, uid, ids, agent_id):
        """al cambiar el agente cargamos sus comisión"""
        result = {}
        v = {}
        if agent_id:
            agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
            v['commission_id'] = agent.commission.id

        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id=False, commission_id=False):
        """al cambiar la comisión comprobamos la selección"""
        result = {}

        if commission_id:
            partner_commission = self.pool.get('commission').browse(cr, uid, commission_id)
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
                    if agent.commission.id !=  partner_commission.id:
                        result['warning'] = {}
                        result['warning']['title'] = _('Fee installments!')
                        result['warning']['message'] = _('A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')

        return result
        

res_partner_agent()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: