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

"""Modificamos las ventas para incluir el comportamiento de comisiones"""

from osv import fields, osv
from tools.translate import _

class sale_order_agent(osv.osv):
    _name = "sale.order.agent"

    def name_get(self, cr, uid, ids, context=None):
        """devuelve como nombre del agente del partner el nombre del agente"""
        if context is None: context = {}
        res = []
        for obj in self.browse(cr, uid, ids):
            res.append((obj.id, obj.agent_id.name))
        return res

    _columns = {
        'sale_id':fields.many2one('sale.order', 'Sale order', required=False, ondelete='cascade', help=''),
        'agent_id':fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id':fields.many2one('commission', 'Applied commission', required=True, ondelete='cascade', help=''),
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

sale_order_agent()

class sale_order(osv.osv):
    """Modificamos las ventas para incluir el comportamiento de comisiones"""

    _inherit = "sale.order"

    _columns = {
        'sale_agent_ids':fields.one2many('sale.order.agent', 'sale_id', 'Agents', states={'draft': [('readonly', False)]})
    }

    def create(self, cr, uid, values, context=None):
        """
        """
        res = super(sale_order, self).create(cr, uid, values, context=context)
        if 'sale_agent_ids' in values:
            for sale_order_agent in values['sale_agent_ids']:
                self.pool.get('sale.order.agent').write(cr, uid, sale_order_agent[1], {'sale_id':res})
        return res

    def write(self, cr, uid, ids, values, context=None):
        """
        """

        if 'sale_agent_ids' in values:
            for sale_order_agent in values['sale_agent_ids']:
                for id in ids:
                    if sale_order_agent[2]:
                        sale_order_agent[2]['sale_id']=id
                    else:
                        self.pool.get('sale.order.agent').unlink(cr, uid, sale_order_agent[1])
        return super(sale_order, self).write(cr, uid, ids, values, context=context)

    def onchange_partner_id(self, cr, uid, ids, part):
        """heredamos el evento de cambio del campo partner_id para actualizar el campo agent_id"""
        sale_agent_ids=[]
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        if res.get('value', False) and part:
            sale_order_agent = self.pool.get('sale.order.agent')
            if ids:
                sale_order_agent.unlink(cr, uid, sale_order_agent.search(cr, uid ,[('sale_id','=',ids)]))
            partner = self.pool.get('res.partner').browse(cr, uid, part)
            for partner_agent in partner.commission_ids:
                vals={
                    'agent_id':partner_agent.agent_id.id,
                    'commission_id':partner_agent.commission_id.id,
                    #'sale_id':ids
                }
                if ids:
                    for id in ids:
                        vals['sale_id']=id
                sale_agent_id=sale_order_agent.create(cr, uid, vals)
                sale_agent_ids.append(int(sale_agent_id))
            res['value']['sale_agent_ids'] =  sale_agent_ids
        return res


    def action_ship_create(self, cr, uid, ids, context=None):
        """extend this method to add agent_id to picking"""
        res = super(sale_order, self).action_ship_create(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids):
            pickings = [x.id for x in order.picking_ids]
            agents = [x.agent_id.id for x in order.sale_agent_ids]
            if pickings and agents:
                self.pool.get('stock.picking').write(cr, uid, pickings, {'agent_ids': [[6, 0, agents]] })
        return res

sale_order()


class sale_order_line(osv.osv):
    """Modificamos las lineas ventas para incluir las comisiones en las facturas creadas desde ventas"""

    _inherit = "sale.order.line"


    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        res = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context)
        so_ref = self.browse(cr,uid,ids)[0].order_id
        for so_agent_id in so_ref.sale_agent_ids:
            inv_lines = self.pool.get('account.invoice.line').browse(cr, uid, res)
            for inv_line in inv_lines:
                if inv_line.product_id and inv_line.product_id.commission_exent != True:
                    vals = {
                        'invoice_line_id': inv_line.id,
                        'agent_id': so_agent_id.agent_id.id,
                        'commission_id': so_agent_id.commission_id.id,
                        'settled': False
                    }
                    line_agent_id=self.pool.get('invoice.line.agent').create(cr, uid, vals)
                    self.pool.get('invoice.line.agent').calculate_commission(cr, uid, [line_agent_id])
        return res

sale_order_line()



