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

"""objeto de comportamiento many2many que relaciona agentes o comerciales con partners"""

# from osv import fields, orm
# from tools.translate import _
from openerp import models, fields, api, _


class res_partner_agent(models.Model):
    """objeto de comportamiento many2many
    que relaciona agentes o comerciales con partners"""
    _name = "res.partner.agent"
    _rec_name = "agent_name"

    def _get_partner_agents_to_update_from_sale_agents(self, cr, uid, ids, context=None):
        """devuelve los ids de partner agents a actualizar
        desde el lanzamiento de un evento de actualización
        en agentes de ventas
        """
        if context is None:
            context = {}
        agent_pool = self.pool.get('res.partner.agent')
        agent_obj_ids = [agent_obj_id.id for agent_obj_id in self.browse(cr, uid, ids, context=context)]
        return agent_pool.search(cr, uid, [('agent_id', 'in', agent_obj_ids)], context=context)

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
        select=1
    )

    agent_id = fields.Many2one(
        "sale.agent",
        string="Agent",
        required=True,
        ondelete="cascade"
    )

    agent_name = fields.Char(
        string="Agent name",
        related="agent_id.name"
    )

    commission_id = fields.Many2one(
        "commission",
        string="Applied commission",
        required=True,
        ondelete="cascade"
    )

    type = fields.Selection(
        string="Type",
        relation="agent_id.type",
        selection=[('asesor', 'Adviser'), ('comercial', 'Commercial')],
        readonly=True,
        # store={
        #     'sale.agent': (_get_partner_agents_to_update_from_sale_agents, ['type'], 10),
        #     'res.partner.agent': (lambda self, cr, uid, ids, c={}: ids, None, 20)
        # }
    )

    def onchange_agent_id(self, cr, uid, ids, agent_id, context=None):
        """al cambiar el agente cargamos sus comisión"""
        result = {}
        v = {}
        if agent_id:
            agent = self.pool.get('sale.agent').browse(cr, uid, agent_id, context=context)
            v['commission_id'] = agent.commission.id
        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id=False, commission_id=False, context=None):
        """al cambiar la comisión comprobamos la selección"""
        if context is None:
            context = {}
        result = {}
        if commission_id:
            partner_commission = self.pool.get('commission').browse(cr, uid, commission_id, context=context)
            if partner_commission.sections and agent_id:
                agent = self.pool.get('sale.agent').browse(cr, uid, agent_id, context=context)
                if agent.commission.id != partner_commission.id:
                    result['warning'] = {
                        'title': _('Fee installments!'),
                        'message': _('A commission has been assigned by sections that does not '
                                     'match that defined for the agent by default, so that these '
                                     'sections shall apply only on this bill.')
                    }
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
