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

from osv import fields, osv


class commission(osv.osv):
    """Objeto comisión"""

    _name = "commission"
    _description = "Commission"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'type': fields.selection((('fijo', 'Fix percentage'), ('tramos', 'By sections')), 'Type', required=True),
        'fix_qty': fields.float('Fix Percentage'),
        'sections': fields.one2many('commission.section', 'commission_id', 'Sections')
    }
    _defaults = {
        'type' : lambda *a: 'fijo',
    }

    def calcula_tramos(self, cr, uid, ids, base):
        commission = self.browse(cr, uid, ids)[0]
        #Cálculo de tramos
        for section in commission.sections:
            if base >= section.commission_from and (base < section.commission_until or section.commission_until == 0):
                res = base * section.percent / 100.0
                return res
        return 0.0

commission()


class commission_section(osv.osv):
    """periodo de las comisiones"""

    _name = "commission.section"
    _description = "Commission section"
    _columns = {
        'commission_from': fields.float('From'),
        'commission_until': fields.float('Until'),
        'percent': fields.float('Percent'),
        'commission_id': fields.many2one('commission', 'Commission')

    }

commission_section()

class sale_agent(osv.osv):
    """Agente de ventas"""

    _name = "sale.agent"
    _description = "Sale agent"

    _columns = {
        'name': fields.char('Saleagent Name', size=125, required=True),
        'type': fields.selection((('asesor', 'Adviser'), ('comercial', 'Commercial')), 'Type', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='cascade', help='Associated partner, is necessary for income invoices.'),
        'code':fields.related ('partner_id','ref', string='Code', readonly=True, type='char', help='Se obtiene del código de la empresa relacionada'),
        'employee_id': fields.many2one('hr.employee', 'Associated Employee', help='Employee associated to agent, is necessary for set an employee to settle commissions in wage.'),
        'customer': fields.one2many('res.partner.agent', 'agent_id', 'Customer', readonly=True),
        'commission': fields.many2one('commission', 'Commission by default', required=True),
        'settlement': fields.selection((('m', 'Monthly'),('t', 'Quarterly'),('s', 'Semiannual'),('a', 'Annual')), 'Period settlement', required=True),
        'active': fields.boolean('Active'),
        'retention_id': fields.many2one ('account.tax', 'Applied retention'),
        'settlement_ids': fields.one2many ('settlement.agent', 'agent_id', 'Settlements executed', readonly=True)
    }
    _defaults = {
        'active': lambda *a: True,
        'type' : lambda *a: 'asesor',
    }

    def calcula_tramos (self, cr, uid, ids, base):
        """calcula los tramos por factura"""
        agente = self.browse(cr, uid, ids)[0]
        return agente.commission.calcula_tramos(base)


sale_agent()#

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

