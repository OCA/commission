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
"""Objetos sobre las liquidación"""

from openerp import models, fields, _
from openerp import tools
from openerp import exceptions


class settlement(models.Model):
    """Settlement model"""

    _name = "settlement"

    name = fields.Char(
        string="Settlement period",
        required=True,
        readonly=True
    )

    total = fields.Float(string="Total", readonly=True)

    date_from = fields.Date(string="From")

    date_to = fields.Date(string="To")

    settlement_agent_id = fields.One2many(
        "settlement.agent",
        "settlement_id",
        string="Settlement agents",
        readonly=True)

    date = fields.Datetime(
        string="Created Date",
        required=True,
        default=fields.Datetime.now()
    )

    # TODO: Workflow is necessary to manage 'cancel' state/transition
    state = fields.Selection(
        [
            ("invoiced", "Invoiced"),
            ("settled", "Settled"),
            ("cancel", "Cancel")
        ],
        string="State",
        readonly=True,
        default="settled"
    )

    def action_invoice_create(self, cursor, user, ids,
                              journal_id, product_id, context=None):
        if context is None:
            context = {}
        agents_pool = self.pool.get('settlement.agent')
        res = {}
        for settlement in self.browse(cursor, user, ids, context=context):
            settlement_agent_ids = map(
                lambda x: x.id, settlement.settlement_agent_id
            )
            invoices_agent = agents_pool.action_invoice_create(
                cursor, user,
                settlement_agent_ids,
                journal_id,
                product_id,
                context=context
            )
            res[settlement.id] = invoices_agent.values()
        return res

    def calculate(self, cr, uid, ids, agent_ids,
                  date_from, date_to, context=None):
        """genera una entrada de liquidación por agente"""
        # Busca todas las líneas de liquidación facturadas en un período
        if context is None:
            context = {}
        sale_agent_pool = self.pool.get('sale.agent')
        settlement_agent_pool = self.pool.get('settlement.agent')
        agents = sale_agent_pool.browse(cr, uid, agent_ids, context=context)
        total = 0
        for agent in agents:
            # genera una entrada de liquidación por agente
            liq_agent_id = settlement_agent_pool.create(
                cr, uid,
                {'agent_id': agent.id, 'settlement_id': ids},
                context=context
            )
            settlement_agent_pool.calculate(
                cr, uid,
                liq_agent_id,
                date_from,
                date_to,
                context=context
            )
            liq_agent = settlement_agent_pool.browse(
                cr, uid,
                liq_agent_id,
                context=context
            )
            total = total + liq_agent.total
        return self.write(cr, uid, ids, {'total': total}, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        """Cancel the liquidation"""
        if context is None:
            context = {}
        agent_pool = self.pool.get('invoice.line.agent')
        for settle in self.browse(cr, uid, ids, context=context):
            for settle_line in settle.settlement_agent_id:
                for line in settle_line.lines:
                    line_id = line.invoice_line_id
                    commissions = [x.id for x in line_id.commission_ids]
                    commission_ids = line.invoice_line_id and commissions or []
                    if commission_ids:
                        agent_pool.write(
                            cr, uid,
                            commission_ids,
                            {'settled': False, 'quantity': 0.0},
                            context=context
                        )
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """permite borrar liquidaciones canceladas"""
        if context is None:
            context = {}
        for settle in self.browse(cr, uid, ids, context=context):
            if settle.state != 'cancel':
                raise exceptions.Warning(
                    _("You can\'t delete it, if it isn't in cancel state.")
                )
        return super(settlement, self).unlink(cr, uid, ids, context=context)


class settlement_agent(models.Model):
    """Liquidaciones de Agentes"""

    _name = 'settlement.agent'

    def _invoice_line_hook(self, cursor, user,
                           move_line, invoice_line_id, context=None):
        '''Call after the creation of the invoice line'''
        return

    def _get_address_invoice(self, cr, uid, settlement, context=None):
        """Return
        {
            'default: address,
            'contact': address,
            'invoice': address
        } for invoice
        """
        if context is None:
            context = {}
        partner_obj = self.pool.get('res.partner')
        partner = settlement.agent_id.partner_id
        return partner_obj.address_get(
            cr, uid,
            [partner.id],
            ['default', 'contact', 'invoice'],
            context=context
        )

    def _invoice_hook(self, cr, uid, picking, invoice_id, context=None):
        '''Call after the creation of the invoice'''
        return

    agent_id = fields.Many2one(
        "sale.agent",
        string="Agent",
        required=True,
        select=1
    )

    total_per = fields.Float(
        string="Total percentages",
        readonly=True
    )
    total_sections = fields.Float(string="Total sections", readonly=True)

    total = fields.Float(string="Total", readonly=True)

    lines = fields.One2many(
        "settlement.line",
        "settlement_agent_id",
        string="Lines",
        readonly=True
    )

    invoices = fields.One2many(
        "settled.invoice.agent",
        "settlement_agent_id",
        string="Invoices",
        readonly=True
    )

    settlement_id = fields.Many2one(
        "settlement",
        string="Settlement",
        required=True,
        ondelete="cascade"
    )

    def get_currency_id(self, cr, uid, picking, context=None):
        return False

    def action_invoice_create(self, cr, uid,
                              ids, journal_id, product_id, context=None):
        '''Return ids of created invoices for the settlements'''
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        product_pool = self.pool.get('product.product')
        account_fiscal_position_pool = self.pool.get('account.fiscal.position')
        res = {}
        for settlement in self.browse(cr, uid, ids, context=context):
            payment_term_id = False
            partner = settlement.agent_id and settlement.agent_id.partner_id
            if not partner:
                raise exceptions.Warning(
                    _('Agent to settle hasn\'t assigned partner.')
                )
            # El tipo es de facura de proveedor
            account_id = partner.property_account_payable.id
            address_default_id, address_contact_id, address_invoice_id = (
                self._get_address_invoice(
                    cr, uid, settlement, context=context
                ).values()
            )

            # No se agrupa
            invoice_vals = {
                'name': settlement.settlement_id.name,
                'origin': (settlement.settlement_id.name or ''),
                'type': 'in_invoice',
                'account_id': account_id,
                'partner_id': partner.id,
                'address_invoice_id': address_invoice_id,
                'address_contact_id': address_contact_id,
                'payment_term': payment_term_id,
                'fiscal_position': partner.property_account_position.id
            }
            cur_id = self.get_currency_id(cr, uid, settlement, context=context)
            if cur_id:
                invoice_vals['currency_id'] = cur_id
            if journal_id:
                invoice_vals['journal_id'] = journal_id
            invoice_id = invoice_obj.create(
                cr, uid, invoice_vals, context=context
            )
            res[settlement.id] = invoice_id
            # El producto se selecciona en el wizard correspondiente
            product = product_pool.browse(cr, uid, product_id, context=context)
            account_id = product.product_tmpl_id.property_account_expense.id
            if not account_id:
                account_id = product.categ_id.property_account_expense_categ.id
            # Cálculo de los impuestos a aplicar
            taxes = product.supplier_taxes_id
            # se añade la retención seleccionada de la ficha del agente
            if settlement.agent_id and settlement.agent_id.retention_id:
                taxes.append(settlement.agent_id.retention_id)
            if settlement.agent_id and settlement.agent_id.partner_id:
                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                    cr,
                    uid,
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
                # set UoS if it's a sale and the picking doesn't have one
                uos_id = False
                account_id = account_fiscal_position_pool.map_account(
                    cr, uid,
                    partner.property_account_position,
                    account_id,
                    context=context)
                invoice_line_id = invoice_line_obj.create(cr, uid, {
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
                }, context=context)
                self._invoice_line_hook(
                    cr, uid, invoice, invoice_line_id, context=context
                )
            invoice_obj.button_compute(
                cr, uid, [invoice_id], context=context,
                set_total=(type in ('in_invoice', 'in_refund'))
            )
            self._invoice_hook(
                cr, uid, settlement, invoice_id, context=context
            )
        return res

    def calculate(self, cr, uid, ids, date_from, date_to, context=None):
        if context is None:
            context = {}
        settlement_line_pool = self.pool.get('settlement.line')
        invoice_line_agent_pool = self.pool.get('invoice.line.agent')
        set_agent = self.browse(cr, uid, ids, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        # Recalculamos todas las lineas sujetas a comision
        sql = """
            SELECT  invoice_line_agent.id FROM account_invoice_line
                INNER JOIN invoice_line_agent
                ON invoice_line_agent.invoice_line_id=account_invoice_line.id
                INNER JOIN account_invoice
                ON account_invoice_line.invoice_id = account_invoice.id
            WHERE invoice_line_agent.agent_id={}
                AND invoice_line_agent.settled=True
                AND account_invoice.state<>'draft'
                AND account_invoice.type='out_invoice'
                AND account_invoice.date_invoice >= '{}'
                AND account_invoice.date_invoice <= '{}'
                AND account_invoice.company_id = {}
            """.format(
            set_agent.agent_id.id,
            date_from,
            date_to,
            user.company_id.id
        )
        cr.execute(sql)
        res = cr.fetchall()
        inv_line_agent_ids = [x[0] for x in res]
        invoice_line_agent_pool .calculate_commission(
            cr, uid, inv_line_agent_ids, context=context
        )
        sql = """
            SELECT  account_invoice_line.id FROM account_invoice_line
            INNER JOIN invoice_line_agent
                ON invoice_line_agent.invoice_line_id=account_invoice_line.id
            INNER JOIN account_invoice
                ON account_invoice_line.invoice_id = account_invoice.id
            WHERE invoice_line_agent.agent_id={}
                AND invoice_line_agent.settled=False
                AND account_invoice.state<>'draft'
                AND account_invoice.type='out_invoice'
                AND account_invoice.date_invoice >= '{}'
                AND account_invoice.date_invoice <= '{}'
                AND account_invoice.company_id = {}""".format(
            set_agent.agent_id.id,
            date_from,
            date_to,
            user.company_id.id
        )
        cr.execute(sql)
        res = cr.fetchall()
        inv_line_ids = [x[0] for x in res]
        total_per = 0
        total_sections = 0
        sections = {}
        for inv_line_id in inv_line_ids:
            linea_id = settlement_line_pool.create(
                cr, uid,
                {'invoice_line_id': inv_line_id, 'settlement_agent_id': ids},
                context=context
            )
            settlement_line_pool.calculate(cr, uid, linea_id, context=context)
            line = settlement_line_pool.browse(
                cr, uid, linea_id, context=context
            )
            # Marca la comision en la factura como liquidada
            # y establece la cantidad
            # Si es por tramos la cantidad será cero,
            # pero se reflejará sobre el tramo del Agente
            if line.commission_id.type == "fijo":
                total_per = total_per + line.commission
                inv_ag_ids = invoice_line_agent_pool.search(
                    cr, uid,
                    [('invoice_line_id', '=', inv_line_id),
                     ('agent_id', '=', set_agent.agent_id.id)],
                    context=context
                )

                invoice_line_agent_pool.write(
                    cr, uid,
                    inv_ag_ids,
                    {'settled': True, 'quantity': line.commission},
                    context=context
                )
            product_id = line.invoice_line_id.product_id
            is_commission_exent = product_id.commission_exent
            if line.commission_id.type == "tramos" and not is_commission_exent:
                # Hacemos un agregado de la base de cálculo agrupándolo
                # por las distintas comisiones en tramos que
                # tenga el agente asignadas
                if line.commission_id.id in sections:
                    sections[line.commission_id.id]['base'] = (
                        sections[line.commission_id.id]['base'] +
                        line.invoice_line_id.price_subtotal
                    )
                    # Añade la línea de la que se añade esta base
                    # para el cálculo por tramos
                    sections[line.commission_id.id]['lines'].append(line)
                else:
                    sections[line.commission_id.id] = {
                        'type': line.commission_id,
                        'base': line.invoice_line_id.price_subtotal,
                        'lines': [line]
                    }
        # Tramos para cada tipo de comisión creados
        for tramo in sections:
            # Cálculo de la comisión  para cada tramo
            tramo = sections[tramo]
            sections[tramo].update(
                {
                    'commission': tramo['type'].calcula_tramos(tramo['base'])
                }
            )
            total_sections = total_sections + sections[tramo]['commission']
            # reparto de la comisión para cada linea
            for linea_tramo in sections[tramo]['lines']:
                subtotal = linea_tramo.invoice_line_id.price_subtotal
                com_por_linea = (sections[tramo]['commission'] *
                                 (subtotal / sections[tramo]['base']))
                linea_tramo.write({'commission': com_por_linea})
                inv_ag_ids = invoice_line_agent_pool.search(cr, uid, [
                    ('invoice_line_id', '=', linea_tramo.invoice_line_id.id),
                    ('agent_id', '=', set_agent.agent_id.id)
                ], context=context)
                invoice_line_agent_pool.write(
                    cr, uid, inv_ag_ids,
                    {'settled': True, 'quantity': com_por_linea},
                    context=context
                )
        total = total_per + total_sections
        self.write(
            cr, uid, ids,
            {
                'total_per': total_per,
                'total_sections': total_sections,
                'total': total
            },
            context=context
        )


class settlement_line(models.Model):
    """Línea de las liquidaciones de los agentes
     Una línea por línea de factura
    """
    _name = "settlement.line"

    def _default_currency(self):
        # BBB: I think this is wrong...
        # sale order o invoice could be in a different currency
        company = self.env.user.company_id
        return company.currency_id.id

    invoice_id = fields.Many2one(
        "account.invoice",
        string="Invoice",
        related="invoice_line_id.invoice_id"
    )

    invoice_date = fields.Date(
        string="Invoice Date",
        related="invoice_id.date_invoice",
        readonly=True
    )

    settlement_agent_id = fields.Many2one(
        "settlement.agent",
        string="Settlement agent",
        required=True,
        select=1,
        ondelete="cascade"
    )
    invoice_line_id = fields.Many2one(
        "account.invoice.line",
        string="Settled invoice line",
        required=True
    )

    amount = fields.Float(string="Invoice line amount", readonly=True)

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
        default=_default_currency
    )
    commission_id = fields.Many2one(
        "commission",
        string="Commission",
        readonly=True
    )
    commission = fields.Float(string="Quantity", readonly=True)

    def calculate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        currency_pool = self.pool.get('res.currency')
        line = self.browse(cr, uid, ids, context=context)
        amount = 0
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        # Recorre los agentes y condiciones asignados a la factura
        for commission in line.invoice_line_id.commission_ids:
            # selecciona el asignado al agente para el que está liquidando
            if commission.agent_id.id == line.settlement_agent_id.agent_id.id:
                commission_app = commission.commission_id  # Obtiene el objeto
                invoice_line_amount = line.invoice_line_id.price_subtotal
                if commission_app.type == "fijo":
                    commission_per = commission_app.fix_qty
                    subtotal = line.invoice_line_id.price_subtotal
                    amount = amount + subtotal * float(commission_per) / 100
                elif commission_app.type == "tramos":
                    invoice_line_amount = 0
                    amount = 0
                invoice_currency_id = line.invoice_id.currency_id.id
                company_currency_id = user.company_id.currency_id.id
                cc_amount_subtotal = (
                    invoice_currency_id != company_currency_id and
                    currency_pool.compute(
                        cr, uid, invoice_currency_id,
                        company_currency_id,
                        invoice_line_amount,
                        round=False,
                        context=context)
                    or
                    invoice_line_amount
                )
                cc_commission_amount = (
                    invoice_currency_id != company_currency_id and
                    currency_pool.compute(
                        cr, uid, invoice_currency_id,
                        company_currency_id,
                        amount,
                        round=False,
                        context=context)
                    or
                    amount
                )
                self.write(
                    cr, uid, ids,
                    {
                        'amount': cc_amount_subtotal,
                        'commission_id': commission_app.id,
                        'commission': cc_commission_amount,
                        'currency_id': user.company_id.currency_id.id
                    }
                )


class settled_invoice_agent(models.Model):
    _name = "settled.invoice.agent"
    _description = "Sale Agents' invoices summary"
    _auto = False

    agent_id = fields.Many2one(
        "sale.agent",
        string="Agent",
        readonly=True,
        select=1
    )

    invoice_id = fields.Many2one(
        "account.invoice",
        string="Invoice",
        readonly=True,
        select=1
    )

    settlement_agent_id = fields.Many2one(
        "settlement.agent",
        string="Agent settl.",
        readonly=True,
        select=1,
        ondelete="cascade"
    )

    invoice_number = fields.Char(
        string="Invoice no",
        related="invoice_id.number",
        readonly=True
    )

    invoice_date = fields.Date(
        string="Invoice date",
        related="invoice_id.date_invoice",
        readonly=True,
        select=1
    )

    invoice_amount = fields.Float(
        string="Amount assigned in invoice",
        readonly=True
    )

    settled_amount = fields.Float(
        string="Settled amount",
        readonly=True
    )

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, "settled_invoice_agent", )
        cr.execute("""
            create or replace view settled_invoice_agent as (
            SELECT (
                account_invoice_line.invoice_id*10000+settlement_agent.agent_id
                ) as id,
                    settlement_agent.id as settlement_agent_id,
                    account_invoice_line.invoice_id as invoice_id,
                    settlement_agent.agent_id as agent_id,
                    sum(settlement_line.amount) as invoice_amount,
                    sum(settlement_line.commission) as settled_amount
            FROM settlement_agent
              INNER JOIN settlement_line
                ON settlement_agent.id = settlement_line.settlement_agent_id
              INNER JOIN account_invoice_line
                ON account_invoice_line.id = settlement_line.invoice_line_id
              GROUP BY
                account_invoice_line.invoice_id,
                settlement_agent.agent_id,
                settlement_agent.id

           )""")
