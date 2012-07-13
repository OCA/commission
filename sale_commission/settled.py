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

"""Objetos sobre las liquidaci??n"""

from osv import fields, osv
from tools.translate import _
import time
import tools

class settled_wizard (osv.osv_memory):
    """settled.wizard"""
    
    _name = 'settled.wizard'
    _columns = {
        #'settlement':fields.selection((('m', 'Monthly'),('t', 'Quarterly'),('s', 'Semiannual'),('a', 'Annual')), 'Settlement period', required=True),
        'date_from':fields.date ('From',required=True),
        'date_to':fields.date ('To',required=True),

    }
    _defaults = {
    }

    def settlement_exec(self, cr, uid, ids, context=None):
        """se ejecuta correctamente desde dos."""
        for o in self.browse(cr, uid, ids, context=context):

            pool_liq = self.pool.get('settlement')
            liq_id = pool_liq.search(cr, uid, [('date_to', '>=', o.date_from)])
            
            vals={
                'name': o.date_from+ " // " + o.date_to,
                'date_from':o.date_from,
                'date_to':o.date_to
            }
            liq_id = pool_liq.create(cr, uid, vals)
            pool_liq.calcula(cr, uid, liq_id, context['active_ids'], o.date_from, o.date_to)


        return {
            'type': 'ir.actions.act_window_close',
        }

      
    def action_cancel(self, cr, uid, ids, conect=None):
        """CANCEL LIQUIDACI??N"""
        return {
            'type': 'ir.actions.act_window_close',
        }

        

settled_wizard()


class recalculate_commision_wizard (osv.osv_memory):
    """settled.wizard"""

    _name = 'recalculate.commission.wizard'
    _columns = {
        'date_from':fields.date ('From',required=True),
        'date_to':fields.date ('To',required=True),

    }
    _defaults = {
    }

    def recalculate_exec(self, cr, uid, ids, context=None):
        """se ejecuta correctamente desde dos."""
        user = self.pool.get('res.users').browse(cr, uid, uid)

        for o in self.browse(cr, uid, ids, context=context):

            sql = 'SELECT  invoice_line_agent.id FROM account_invoice_line ' \
              'INNER JOIN invoice_line_agent ON invoice_line_agent.invoice_line_id=account_invoice_line.id ' \
              'INNER JOIN account_invoice ON account_invoice_line.invoice_id = account_invoice.id ' \
              'WHERE invoice_line_agent.agent_id in (' + ",".join(map(str, context['active_ids'])) + ') AND invoice_line_agent.settled=False ' \
              'AND account_invoice.state<>\'draft\' AND account_invoice.type=\'out_invoice\''\
              'AND account_invoice.date_invoice >= \'' + o.date_from + '\' AND account_invoice.date_invoice <= \'' + o.date_to +'\''\
              ' AND account_invoice.company_id = ' + str(user.company_id.id)

            cr.execute(sql)
            res = cr.fetchall()
            inv_line_agent_ids = [x[0] for x in res]

            self.pool.get ('invoice.line.agent').calculate_commission( cr, uid, inv_line_agent_ids)


        return {
            'type': 'ir.actions.act_window_close',
        }


    def action_cancel(self, cr, uid, ids, conect=None):
        """CANCEL CALCULATE"""
        return {
            'type': 'ir.actions.act_window_close',
        }



recalculate_commision_wizard()




class settlement (osv.osv):
    """Objeto Liquidaci??n"""

    _name = 'settlement'
    _columns = {
        'name': fields.char('Settlement period', size=64, required=True, readonly=True),
        'total': fields.float('Total', readonly=True),
        'date_from':fields.date('From'),
        'date_to':fields.date('To'),
        'settlement_agent_id': fields.one2many('settlement.agent', 'settlement_id', 'Settlement agents', readonly=True),
        'date': fields.datetime('Created Date', required=True),
        'state': fields.selection([('invoiced', 'Invoiced'),('settled', 'Settled'), ('cancel', 'Cancel')], 'State', required=True, readonly=True)
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': lambda *a: 'settled'
    }

    def action_invoice_create(self, cursor, user, ids, journal_id, product_id, context=None):

        agents_pool=self.pool.get('settlement.agent')
        res={}
        for settlement in self.browse(cursor, user, ids, context=context):
            settlement_agent_ids = map(lambda x: x.id, settlement.settlement_agent_id)
            invoices_agent = agents_pool.action_invoice_create(cursor, user, settlement_agent_ids, journal_id, product_id)

            res[settlement.id] = invoices_agent.values()
        return res

            


    def calcula(self, cr, uid, ids, agent_ids, date_from, date_to):
        """genera una entrada de liquidaci??n por agente"""

         # Busca todas las l??neas de liquidaci??n facturadas en un per??odo
        pool_agent = self.pool.get('sale.agent')
        agents = pool_agent.browse(cr, uid, agent_ids)
        total = 0
        for agent in agents:
            # genera una entrada de liquidaci??n por agente
            liq_agent_id = self.pool.get('settlement.agent').create(cr, uid, {'agent_id': agent.id, 'settlement_id': ids})
            self.pool.get('settlement.agent').calcula(cr, uid, liq_agent_id, date_from, date_to)
            liq_agent = self.pool.get('settlement.agent').browse(cr, uid, liq_agent_id)
            total = total + liq_agent.total
            
        return self.write (cr, uid, ids, {'total': total})

    def action_cancel(self, cr, uid, ids, context=None):
        """Cancela la liquidaci??n"""
        if context is None: context={}
        for settle in self.browse(cr, uid, ids):
            for settle_line in settle.settlement_agent_id:
                for line in settle_line.lines:
                    commission_ids = line.invoice_line_id and [x.id for x in line.invoice_line_id.commission_ids] or []
                    if commission_ids:
                        self.pool.get('invoice.line.agent').write(cr, uid, commission_ids, {'settled': False, 'quantity': 0.0})

        return self.write(cr, uid, ids, {'state': 'cancel'})

    def unlink(self, cr, uid, ids, context=None):
        """permite borrar liquidaciones canceladas"""
        for settle in self.browse(cr, uid, ids):
            if settle.state != 'cancel':
                raise osv.except_osv(_('Error!'), _("You can\'t delete it, if it isn't in cancel state."))

        return super(settlement, self).unlink(cr, uid, ids, context=context)

settlement()


class settlement_agent (osv.osv):
    """Liquidaciones de Agentes"""

    _name = 'settlement.agent'

    def _invoice_line_hook(self, cursor, user, move_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        return

    def _get_address_invoice(self, cursor, user, settlement):
        '''Return {'contact': address, 'invoice': address} for invoice'''
        partner_obj = self.pool.get('res.partner')
        partner = settlement.agent_id.partner_id

        return partner_obj.address_get(cursor, user, [partner.id],
                ['contact', 'invoice'])

    def _invoice_hook(self, cursor, user, picking, invoice_id):
        '''Call after the creation of the invoice'''
        return

    
    _columns = {
        'agent_id': fields.many2one('sale.agent', 'Agent', required=True, select=1),
        'total_per': fields.float('Total percentages', readonly=True),
        'total_sections': fields.float('Total sections', readonly=True),
        'total': fields.float('Total', readonly=True),
        'lines': fields.one2many('settlement.line', 'settlement_agent_id', 'Lines', readonly=True),
        'invoices': fields.one2many('settled.invoice.agent', 'settlement_agent_id', 'Invoices', readonly=True),
        'settlement_id': fields.many2one('settlement', 'Settlement', required=True, ondelete="cascade")
    }



    def get_currency_id(self, cursor, user, picking):
        return False


    def action_invoice_create(self, cursor, user, ids, journal_id, product_id, context=None):
        '''Return ids of created invoices for the settlements'''

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoices_group = {}
        res = {}

        for settlement in self.browse(cursor, user, ids, context=context):

            payment_term_id = False
            partner = settlement.agent_id and settlement.agent_id.partner_id
            if not partner:
                raise osv.except_osv(_('Error, partner fail !'),
                    _('Agent to settle hasn\'t assigned partner.'))

           #El tipo es de facura de proveedor
            account_id = partner.property_account_payable.id

            address_contact_id, address_invoice_id = \
                    self._get_address_invoice(cursor, user, settlement).values()

            # No se agrupa

            invoice_vals = {
                'name': settlement.settlement_id.name,
                'origin': (settlement.settlement_id.name or '') ,
                'type': 'in_invoice',
                'account_id': account_id,
                'partner_id': partner.id,
                'address_invoice_id': address_invoice_id,
                'address_contact_id': address_contact_id,
                #'comment': comment,
                'payment_term': payment_term_id,
                'fiscal_position': partner.property_account_position.id
                }
            cur_id = self.get_currency_id(cursor, user, settlement)
            if cur_id:
                invoice_vals['currency_id'] = cur_id
            if journal_id:
                invoice_vals['journal_id'] = journal_id
            invoice_id = invoice_obj.create(cursor, user, invoice_vals,
                    context=context)


            res[settlement.id] = invoice_id
            # El producto se selecciona en el wizard correspondiente
            product = self.pool.get('product.product').browse(cursor,user,product_id)
            account_id = product.product_tmpl_id.property_account_expense.id
            if not account_id:
                account_id = product.categ_id.property_account_expense_categ.id
            # C??lculo de los impuestos a aplicar

            taxes = product.supplier_taxes_id

            # se a??ade la retenci??n seleccionada de la ficha del agente
            if settlement.agent_id and settlement.agent_id.retention_id:
                taxes.append(settlement.agent_id.retention_id)
            if  settlement.agent_id and settlement.agent_id.partner_id:
                 tax_ids = self.pool.get('account.fiscal.position').map_tax(
                    cursor,
                    user,
                    settlement.agent_id.partner_id.property_account_position,
                    taxes
                )
            else:
                tax_ids = map(lambda x: x.id, taxes)
            for invoice in settlement.invoices:
                origin = invoice.invoice_number
                name = invoice.invoice_number
                price_unit = invoice.settled_amount
                discount = 0

                #set UoS if it's a sale and the picking doesn't have one
                uos_id =  False

                account_id = self.pool.get('account.fiscal.position').map_account(cursor, user, partner.property_account_position, account_id)
                invoice_line_id = invoice_line_obj.create(cursor, user, {
                    'name': name,
                    'origin': origin,
                    'invoice_id': invoice_id,
                    'uos_id': uos_id,
                    'product_id': product.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'discount': discount,
                    'quantity': 1,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    #'account_analytic_id': account_analytic_id,
                    }, context=context)
                self._invoice_line_hook(cursor, user, invoice, invoice_line_id)

            invoice_obj.button_compute(cursor, user, [invoice_id], context=context,
                    set_total=(type in ('in_invoice', 'in_refund')))
            self._invoice_hook(cursor, user, settlement, invoice_id)
        return res

    def calcula(self, cr, uid, ids, date_from, date_to):
        set_agent = self.browse(cr, uid, ids)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        # Recalculamos todas las lineas sujetas a comision

        sql = 'SELECT  invoice_line_agent.id FROM account_invoice_line ' \
              'INNER JOIN invoice_line_agent ON invoice_line_agent.invoice_line_id=account_invoice_line.id ' \
              'INNER JOIN account_invoice ON account_invoice_line.invoice_id = account_invoice.id ' \
              'WHERE invoice_line_agent.agent_id=' + str(set_agent.agent_id.id) + ' AND invoice_line_agent.settled=True ' \
              'AND account_invoice.state<>\'draft\' AND account_invoice.type=\'out_invoice\''\
              'AND account_invoice.date_invoice >= \'' + date_from + '\' AND account_invoice.date_invoice <= \'' + date_to +'\''\
              ' AND account_invoice.company_id = ' + str(user.company_id.id)

        cr.execute(sql)
        res = cr.fetchall()
        inv_line_agent_ids = [x[0] for x in res]

        self.pool.get ('invoice.line.agent').calculate_commission( cr, uid, inv_line_agent_ids)

        sql = 'SELECT  account_invoice_line.id FROM account_invoice_line ' \
              'INNER JOIN invoice_line_agent ON invoice_line_agent.invoice_line_id=account_invoice_line.id ' \
              'INNER JOIN account_invoice ON account_invoice_line.invoice_id = account_invoice.id ' \
              'WHERE invoice_line_agent.agent_id=' + str(set_agent.agent_id.id) + ' AND invoice_line_agent.settled=False ' \
              'AND account_invoice.state<>\'draft\' AND account_invoice.type=\'out_invoice\''\
              'AND account_invoice.date_invoice >= \'' + date_from + '\' AND account_invoice.date_invoice <= \'' + date_to +'\''\
              ' AND account_invoice.company_id = ' + str(user.company_id.id)
       
        cr.execute(sql)
        res = cr.fetchall()
        inv_line_ids = [x[0] for x in res]
        total_per = 0
        total_sections = 0
        total = 0
        sections = {}
        for inv_line_id in inv_line_ids:
            linea_id = self.pool.get('settlement.line').create(cr, uid, {'invoice_line_id': inv_line_id, 'settlement_agent_id': ids})
            self.pool.get('settlement.line').calcula(cr, uid, linea_id)

            line = self.pool.get('settlement.line').browse(cr, uid, linea_id)

            # Marca la comision en la factura como liquidada y establece la cantidad
            # Si es por tramos la cantidad ser?? cero, pero se reflejar?? sobre el tramo del Agente
            

            if line.commission_id.type == "fijo":
                total_per = total_per + line.commission
                inv_ag_ids = self.pool.get('invoice.line.agent').search(cr, uid, [('invoice_line_id', '=', inv_line_id), ('agent_id', '=', set_agent.agent_id.id)])
                self.pool.get('invoice.line.agent').write(cr, uid, inv_ag_ids, {'settled': True, 'quantity': line.commission})
            if line.commission_id.type == "tramos":
                if line.invoice_line_id.product_id.commission_exent != True:
                    # Hacemos un agregado de la base de c??lculo agrup??ndolo por las distintas comisiones en tramos que tenga el agente asignadas
                    if  line.commission_id.id in sections:
                        sections[line.commission_id.id]['base'] = sections[line.commission_id.id]['base'] + line.invoice_line_id.price_subtotal
                        sections[line.commission_id.id]['lines'].append(line)                   # A??ade la l??nea de la que se a??ade esta base para el c??lculo por tramos
                    else:
                        sections[line.commission_id.id] = {'type': line.commission_id, 'base':line.invoice_line_id.price_subtotal, 'lines':[line]}

        #Tramos para cada tipo de comisi??n creados 

        for tramo in sections:
            #C??lculo de la comisi??n  para cada tramo
            sections[tramo].update({'commission': sections[tramo]['type'].calcula_tramos(sections[tramo]['base'])})
            total_sections = total_sections+sections[tramo]['commission']
            # reparto de la comisi??n para cada linea
            
            for linea_tramo in  sections[tramo]['lines']:
                com_por_linea = sections[tramo]['commission']* (linea_tramo.invoice_line_id.price_subtotal/sections[tramo]['base'])
                linea_tramo.write({'commission':com_por_linea})
                inv_ag_ids = self.pool.get('invoice.line.agent').search(cr, uid, [('invoice_line_id', '=', linea_tramo.invoice_line_id.id), ('agent_id', '=', set_agent.agent_id.id)])
                self.pool.get('invoice.line.agent').write(cr, uid, inv_ag_ids, {'settled': True, 'quantity': com_por_linea})
            

        total = total_per + total_sections
        self.write (cr, uid, ids, {'total_per': total_per, 'total_sections': total_sections, 'total': total})

settlement_agent()

class settlement_line (osv.osv):
    """L??nea de las liquidaciones de los agentes
     Una l??nea por l??nea de factura 
    """

    _name = 'settlement.line'
    _columns = {
        'invoice_id':fields.related('invoice_line_id', 'invoice_id', type='many2one', relation='account.invoice', string='Invoice'),
        'invoice_date':fields.related('invoice_id','date_invoice', type='date', readonly=True, string='Invoice Date'),
        'settlement_agent_id': fields.many2one('settlement.agent', 'Settlement agent', required=True, select=1, ondelete="cascade"),
        'invoice_line_id': fields.many2one('account.invoice.line', 'Settled invoice line', required=True),
        'amount': fields.float('Invoice line amount', readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
        'commission_id': fields.many2one('commission', 'Commission', readonly=True),
        'commission': fields.float('Quantity', readonly=True),
    }

    _defaults = {
        'currency_id': lambda self,cr,uid,context: self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
    }

    def calcula(self, cr, uid, ids):
        line = self.browse(cr, uid, ids)
        amount=0
        user = self.pool.get('res.users').browse(cr, uid, uid)

        for commission in line.invoice_line_id.commission_ids:  # Recorre los agentes y condiciones asignados a la factura
            if commission.agent_id.id == line.settlement_agent_id.agent_id.id: # selecciona el asignado al agente para el que est?? liquidando
                commission_app = commission.commission_id                                     # Obtiene el objeto
                invoice_line_amount = line.invoice_line_id.price_subtotal
                if commission_app.type=="fijo":
                    commission_per = commission_app.fix_qty
                    amount = amount + line.invoice_line_id.price_subtotal * float(commission_per) / 100

                elif commission_app.type=="tramos":
                    invoice_line_amount = 0
                    amount = 0

                cc_amount_subtotal = line.invoice_id.currency_id.id != user.company_id.currency_id.id and self.pool.get('res.currency').compute(cr, uid, line.invoice_id.currency_id.id, user.company_id.currency_id.id, invoice_line_amount, round = False) or invoice_line_amount
                cc_commission_amount = line.invoice_id.currency_id.id != user.company_id.currency_id.id and self.pool.get('res.currency').compute(cr, uid, line.invoice_id.currency_id.id, user.company_id.currency_id.id, amount, round = False) or amount

                self.write(cr, uid, ids, {'amount': cc_amount_subtotal, 'commission_id': commission_app.id, 'commission': cc_commission_amount, 'currency_id': user.company_id.currency_id.id})

settlement_line()



class settled_invoice_agent(osv.osv):
    _name = "settled.invoice.agent"
    _description = "Resumen de facturas liquidadas"
    _auto = False
    _columns = {
        'agent_id':fields.many2one('sale.agent', 'Agent', readonly=True, select=1),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True, select=1),
        'settlement_agent_id': fields.many2one('settlement.agent', 'Agent settl.', readonly=True, select=1, ondelete="cascade"),
        'invoice_number':fields.related('invoice_id', 'number', type='char', string='Invoice no', readonly=True ),
        'invoice_date':fields.related('invoice_id', 'date_invoice', string ='Invoice date', type='date', readonly=True, select=1 ),
        'invoice_amount':fields.float( 'Amount assigned in invoice', readonly=True),
        'settled_amount':fields.float('Settled amount', readonly=True),
        #'currency_id': fields.many2one('res.currency', 'Currency', readonly=True, select="1")
    }


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr,  "settled_invoice_agent")
        
        cr.execute("""
            create or replace view settled_invoice_agent as (
            SELECT  (account_invoice_line.invoice_id*10000+settlement_agent.agent_id) as id, settlement_agent.id as settlement_agent_id,
            account_invoice_line.invoice_id as invoice_id, settlement_agent.agent_id as agent_id,
            sum(settlement_line.amount) as invoice_amount,
            sum(settlement_line.commission) as settled_amount
            FROM settlement_agent
              INNER JOIN settlement_line ON settlement_agent.id = settlement_line.settlement_agent_id
              INNER JOIN account_invoice_line ON account_invoice_line.id = settlement_line.invoice_line_id
              GROUP BY account_invoice_line.invoice_id, settlement_agent.agent_id, settlement_agent.id

           )""")

settled_invoice_agent()
