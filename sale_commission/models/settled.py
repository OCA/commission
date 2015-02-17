# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
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

from openerp import models, fields, api, _, exceptions
from openerp import tools


class settlement(models.Model):
    """Settlement model"""
    _name = "settlement"
    name = fields.Char(string="Settlement period", required=True,
                       readonly=True)
    total = fields.Float(string="Total", readonly=True)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    settlement_agent_id = fields.One2many("settlement.agent", "settlement_id",
                                          string="Settlement agents",
                                          readonly=True)
    date = fields.Datetime(string="Created Date", required=True,
                           default=fields.Datetime.now())
    # TODO: Workflow is necessary to manage 'cancel' state/transition
    state = fields.Selection([("invoiced", "Invoiced"),
                              ("settled", "Settled"),
                              ("cancel", "Cancel")], string="State",
                             readonly=True, default="settled")

    def action_invoice_create(self, journal_id, product_id):
        res = {}
        for settlement in self.browse(self._context['active_ids']):
            for settle_agent in settlement.settlement_agent_id:
                invoices_agent = settle_agent.action_invoice_create(
                    journal_id, product_id)
            res[settlement.id] = invoices_agent.values()
        return res

    @api.one
    def calculate(self, agent_ids, date_from, date_to):
        """generate one settlement line per agent"""
        # Search for all settlements in a period
        sale_agent_pool = self.env['sale.agent']
        settlement_agent_pool = self.env['settlement.agent']
        agents = sale_agent_pool.browse(agent_ids)
        total = 0
        for agent in agents:
            # generate one settlement line per agent
            liq_agent = settlement_agent_pool.create(
                {'agent_id': agent.id, 'settlement_id': self.id})
            liq_agent.calculate(date_from, date_to)
            total = total + liq_agent.total
        return self.write({'total': total})

    @api.multi
    def action_cancel(self):
        """Cancel the liquidation"""
        for settle in self:
            for settle_line in settle.settlement_agent_id:
                for line in settle_line.lines:
                    line_id = line.invoice_line_id
                    commissions = line_id.commission_ids
                    for commission in commissions:
                        commission.write({'settled': False, 'quantity': 0.0})
            settle.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        """Allow to delete cancelled settlements"""
        for settle in self:
            if settle.state != 'cancel':
                raise exceptions.Warning(
                    _("You can't delete it, if it isn't in cancel state.")
                )
        return super(settlement, self).unlink()


class settlement_agent(models.Model):
    """Agent's settlement"""
    _name = 'settlement.agent'

    def _invoice_line_hook(self, invoice_line):
        '''Call after the creation of the invoice line'''
        return

    @api.multi
    def _get_address_invoice(self):
        """Return
        {'default: address,
        'contact': address,
        'invoice': address
        } for invoice
        """
        self.ensure_one()
        partner = self.agent_id.partner_id
        return partner.address_get(['default', 'contact', 'invoice'])

    def _invoice_hook(self, invoice):
        '''Call after the creation of the invoice'''
        return

    agent_id = fields.Many2one("sale.agent", string="Agent", required=True,
                               select=1)
    total_per = fields.Float("Total percentages", readonly=True)
    total_sections = fields.Float(string="Total sections", readonly=True)
    total = fields.Float(string="Total", readonly=True)
    lines = fields.One2many("settlement.line", "settlement_agent_id",
                            string="Lines", readonly=True)
    invoices = fields.One2many("settled.invoice.agent", "settlement_agent_id",
                               string="Invoices", readonly=True)
    settlement_id = fields.Many2one("settlement", string="Settlement",
                                    required=True, ondelete="cascade")

    def get_currency_id(self):
        return False

    @api.multi
    def action_invoice_create(self, journal, product):
        '''Return ids of created invoices for the settlements'''
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        res = {}
        for settlement in self:
            payment_term_id = False
            partner = settlement.agent_id and settlement.agent_id.partner_id
            if not partner:
                raise exceptions.Warning(
                    _("Agent to settle hasn't assigned partner.")
                )
            # Invoice is from a supplier
            account_id = partner.property_account_payable.id
            address_default_id, address_contact_id, address_invoice_id = (
                settlement._get_address_invoice().values())
            # Don't group
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
            cur_id = settlement.get_currency_id()
            if cur_id:
                invoice_vals['currency_id'] = cur_id
            if journal:
                invoice_vals['journal_id'] = journal.id
            invoice = invoice_obj.create(invoice_vals)
            res[settlement.id] = invoice.id
            # The product is chosen in the appropriate wizard
            account_id = product.product_tmpl_id.property_account_expense.id
            if not account_id:
                account_id = product.categ_id.property_account_expense_categ.id
            # Tax calculations to be applied
            taxes = []
            if product.supplier_taxes_id:
                taxes.append(product.supplier_taxes_id)
            # Append the retention associated to the agent
            if settlement.agent_id and settlement.agent_id.retention_id:
                taxes.append(settlement.agent_id.retention_id)
            if settlement.agent_id and settlement.agent_id.partner_id:
                pap = settlement.agent_id.partner_id.property_account_position
                tax_ids = pap.map_tax(taxes).ids
            else:
                tax_ids = map(lambda x: x.id, taxes).ids
            for set_invoice in settlement.invoices:
                origin = set_invoice.invoice_number
                name = set_invoice.invoice_number
                price_unit = set_invoice.settled_amount
                discount = 0
                # set UoS if it's a sale and the picking doesn't have one
                uos_id = False
                account_id = (
                    partner.property_account_position.map_account(account_id))
                invoice_line = invoice_line_obj.create({
                    'name': name,
                    'origin': origin,
                    'invoice_id': invoice.id,
                    'uos_id': uos_id,
                    'product_id': product.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'discount': discount,
                    'quantity': 1,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                })
                settlement._invoice_line_hook(invoice_line)
            invoice.button_compute(
                set_total=(type in ('in_invoice', 'in_refund')))
            settlement._invoice_hook(invoice)
        return res

    @api.one
    def calculate(self, date_from, date_to):
        settlement_line_pool = self.env['settlement.line']
        invoice_line_agent_pool = self.env['invoice.line.agent']
        invoice_obj = self.env['account.invoice']
        involine_obj = self.env['account.invoice.line']
        user = self.env.user
        # Recalculate all the line that has commission
        invoice_id_lst = invoice_obj.search(
            [('state', '!=', 'draft'), ('type', '=', 'out_invoice'),
             ('date_invoice', '>=', date_from),
             ('date_invoice', '<=', date_to),
             ('company_id', '=', user.company_id.id)]).ids
        invoice_lines = involine_obj.search(
            [('invoice_id', 'in', invoice_id_lst)])
        inv_line_agents = invoice_line_agent_pool.search(
            [('invoice_line_id', 'in', invoice_lines.ids),
             ('settled', '=', True)])
        for inv_line_agent in inv_line_agents:
            inv_line_agent.calculate_commission()
        # search no settled agent lines
        inv_line_nos_agents = invoice_line_agent_pool.search(
            [('invoice_line_id', 'in', invoice_lines.ids),
             ('settled', '=', False)])
        total_per = 0
        total_sections = 0
        sections = {}
        for inv_line in inv_line_nos_agents.invoice_line_id:
            settle_line = settlement_line_pool.create(
                {'invoice_line_id': inv_line.id,
                 'settlement_agent_id': self.id})
            settle_line.calculate()
            # Mark the commission in the invoice as settled
            # and calculate the quantity
            # If we use sections then the quantity is zero,
            # although will reflect the Agent
            if settle_line.commission_id.commission_type == "fixed":
                total_per = total_per + settle_line.commission
                inv_ag_lst = invoice_line_agent_pool.search(
                    [('invoice_line_id', '=', inv_line.id),
                     ('agent_id', '=', self.agent_id.id)])
                for inv_agent in inv_ag_lst:
                    inv_agent.write({'settled': True,
                                     'quantity': settle_line.commission})
            product_id = settle_line.invoice_line_id.product_id
            is_commission_free = product_id.commission_free
            if (settle_line.commission_id.commission_type == "section" and
                    not is_commission_free):
                # We aggregate the base value by grouping
                # by the distinct sections that the agent
                # has assigned for it
                if settle_line.commission_id.id in sections:
                    sections[settle_line.commission_id.id]['base'] = (
                        sections[settle_line.commission_id.id]['base'] +
                        settle_line.invoice_line_id.price_subtotal
                    )
                    # Append the lines for the calculation by sections
                    commision_id = settle_line.commission_id.id
                    sections[commision_id]['lines'].append(settle_line)
                else:
                    sections[settle_line.commission_id.id] = {
                        'commission_type': settle_line.commission_id,
                        'base': settle_line.invoice_line_id.price_subtotal,
                        'lines': [settle_line]
                    }
        # Iterate over each section created
        for tramo in sections:
            # Calculate the commission for each section
            tramo = sections[tramo]
            sections[tramo].update(
                {'commission': tramo['commission_type'].calculate_section(
                    tramo['base'])})
            total_sections = total_sections + sections[tramo]['commission']
            # Split the commission for each line
            for linea_tramo in sections[tramo]['lines']:
                subtotal = linea_tramo.invoice_line_id.price_subtotal
                com_por_linea = (sections[tramo]['commission'] *
                                 (subtotal / sections[tramo]['base']))
                linea_tramo.write({'commission': com_por_linea})
                inv_ag_lst = invoice_line_agent_pool.search(
                    [('invoice_line_id', '=', linea_tramo.invoice_line_id.id),
                     ('agent_id', '=', self.agent_id.id)])
                for inv_ag in inv_ag_lst:
                    inv_ag.write({'settled': True, 'quantity': com_por_linea})
        total = total_per + total_sections
        self.write({'total_per': total_per, 'total_sections': total_sections,
                    'total': total})


class settlement_line(models.Model):
    """ Settlement line for the agents One line per invoice"""
    _name = "settlement.line"

    def _default_currency(self):
        # BBB: I think this is wrong...
        # sale order o invoice could be in a different currency
        company = self.env.user.company_id
        return company.currency_id.id

    invoice_id = fields.Many2one("account.invoice", string="Invoice",
                                 related="invoice_line_id.invoice_id")
    invoice_date = fields.Date(string="Invoice Date",
                               related="invoice_id.date_invoice",
                               readonly=True)
    settlement_agent_id = fields.Many2one("settlement.agent",
                                          string="Settlement agent",
                                          required=True, select=1,
                                          ondelete="cascade")
    invoice_line_id = fields.Many2one("account.invoice.line",
                                      string="Settled invoice line",
                                      required=True)
    amount = fields.Float(string="Invoice line amount", readonly=True)
    currency_id = fields.Many2one("res.currency", string="Currency",
                                  readonly=True, default=_default_currency)
    commission_id = fields.Many2one("commission", string="Commission",
                                    readonly=True)
    commission = fields.Float(string="Quantity", readonly=True)

    def calculate(self):
        amount = 0
        user = self.env.user
        # Iterate over the agents and commission in the invoice
        for commission in self.invoice_line_id.commission_ids:
            # Check if the agent correspond to the one was settled
            if commission.agent_id.id == self.settlement_agent_id.agent_id.id:
                commission_app = commission.commission_id  # Get the object
                invoice_line_amount = self.invoice_line_id.price_subtotal
                if commission_app.commission_type == "fixed":
                    commission_per = commission_app.fix_qty
                    subtotal = self.invoice_line_id.price_subtotal
                    amount = amount + subtotal * float(commission_per) / 100
                elif commission_app.commission_type == "section":
                    invoice_line_amount = 0
                    amount = 0
                invoice_currency = self.invoice_id.currency_id
                company_currency = user.company_id.currency_id
                cc_amount_subtotal = (
                    invoice_currency != company_currency and
                    invoice_currency.compute(company_currency.id,
                                             invoice_line_amount,
                                             round=False)
                    or
                    invoice_line_amount
                )
                cc_commission_amount = (
                    invoice_currency != company_currency and
                    invoice_currency.compute(company_currency.id, amount,
                                             round=False,)
                    or
                    amount
                )
                self.write({'amount': cc_amount_subtotal,
                            'commission_id': commission_app.id,
                            'commission': cc_commission_amount,
                            'currency_id': user.company_id.currency_id.id
                            }
                           )


class settled_invoice_agent(models.Model):
    _name = "settled.invoice.agent"
    _description = "Sale Agents' invoices summary"
    _auto = False

    agent_id = fields.Many2one("sale.agent", string="Agent", readonly=True,
                               select=1)
    invoice_id = fields.Many2one("account.invoice", string="Invoice",
                                 readonly=True, select=1)
    settlement_agent_id = fields.Many2one(
        "settlement.agent", string="Agent settl.", readonly=True, select=1,
        ondelete="cascade")
    invoice_number = fields.Char(string="Invoice no",
                                 related="invoice_id.number", readonly=True)
    invoice_date = fields.Date(string="Invoice date",
                               related="invoice_id.date_invoice",
                               readonly=True, select=1)
    invoice_amount = fields.Float(
        string="Amount assigned in invoice", readonly=True)
    settled_amount = fields.Float(string="Settled amount", readonly=True)

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
