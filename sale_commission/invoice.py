# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Inform??ticos (<http://www.pexego.es>). All Rights Reserved
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

"""invoice agents"""

from osv import fields, osv
from tools.translate import _

class invoice_line_agent(osv.osv):
    """invoice agents"""

    _name = "invoice.line.agent"

    _columns = {
        'invoice_line_id':fields.many2one('account.invoice.line', 'Invoice Line', required=True, ondelete='cascade', help=''),
        'invoice_id':fields.related('invoice_line_id', 'invoice_id', type='many2one', relation='account.invoice', string='Invoice'),
        'invoice_date':fields.related('invoice_id',type='date_invoice', readonly=True),
        'agent_id': fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id':fields.many2one('commission', 'Applied commission', required=True, ondelete='cascade', help=''),
        'settled':fields.boolean('Settled', readonly=True),
        'quantity':fields.float('Settled amount')
    }
    _defaults = {
        'settled': lambda *a: False,
        'quantity':lambda *a: 0
     }


    def calculate_commission (self, cr, uid, ids):
        for line_agent in self.browse(cr,uid,ids):
             if  line_agent.commission_id.type == 'fijo' and line_agent.commission_id.fix_qty:
                quantity = line_agent.invoice_line_id.price_subtotal * (line_agent.commission_id.fix_qty / 100.0)
                self.write(cr,uid,line_agent.id, {'quantity':quantity})

    def onchange_agent_id(self, cr, uid, ids, agent_id):
        """al cambiar el agente se le carga la comisi??n"""
        result = {}
        v = {}
        if agent_id:
            agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
            v['commission_id'] = agent.commission.id
            agent_line = self.browse(cr, uid, ids)
            if agent_line:
                v['quantity'] = agent_line[0].invoice_line_id.price_subtotal * (agent.commission.fix_qty / 100.0)
            else:
                v['quantity'] = 0

        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id, commission_id):
        """alerta al usuario sobre la comisi??n elegida"""
        result = {}
        v = {}
        if commission_id:
            partner_commission = self.pool.get('commission').browse(cr, uid, commission_id)
            agent_line = self.browse(cr, uid, ids)
            v['quantity'] = agent_line[0].invoice_line_id.price_subtotal * (partner_commission.fix_qty / 100.0)
            result['value']=v
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
                    
                    if agent.commission.id !=  partner_commission.id:
                        result['warning'] = {}
                        result['warning']['title'] = _('Fee installments!')
                        #result['warning']['message'] = 'Se ha asignado una comisi??n por tramos que no coincide con la definida para el agente por defecto, por lo que estos tramos se aplicar??n tan solo sobre esta factura.'
                        result['warning']['message'] = _('A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')
        return result


invoice_line_agent()

class account_invoice_line(osv.osv):
    """Enlazamos las comisiones a la factura"""

    _inherit = "account.invoice.line"

    _columns = {
        'commission_ids': fields.one2many('invoice.line.agent', 'invoice_line_id', 'Commissions', help="Commissions asociated to invoice line."),
    }

account_invoice_line()

class account_invoice(osv.osv):
    """heredamos las facturas para a??adirles el representante de venta"""

    _inherit = "account.invoice"

    _columns = {
        'agent_id': fields.many2one('sale.agent', 'Agent'),
        'agent_code':fields.related ('agent_id', 'code', readonly=True, type='char', string='Agent code' ),
        'country':fields.related ('partner_id', 'country_id', readonly=True, type='many2one', string= 'Country', relation='res.country' ),
    }

    def onchange_partner_id(self, cr, uid, ids, type, part, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        """Al cambiar la empresa nos treamos el representante asociado a la empresa"""
        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, part, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)

        if part and res.get('value', False):
            partner = self.pool.get('res.partner').browse(cr, uid, part)
            if partner.commission_ids:
                res['value']['agent_id'] = partner.commission_ids[0].agent_id.id

        return res

    def _refund_cleanup_lines(self, cr, uid, lines):
        """ugly function to map all fields of account.invoice.line when creates refund invoice"""
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        for line in res:
            if 'commission_ids' in line[2]:
                line[2]['commission_ids'] = [(6,0, line[2].get('commission_ids', [])) ]
            
        return res

account_invoice()
