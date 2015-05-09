# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Abstract (http://www.abstract.it)
#    @author Davide Corio <davide.corio@abstract.it>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields


class Commission(models.Model):
    _inherit = 'commission'

    commission_type = fields.Selection(
        (("fixed", "Fix percentage"),
            ("section", "By sections"),
            ("formula", "Formula")))

    formula = fields.Text(
        'Formula',
        default="""# variables available:\n# base: invoice line amount\
(untaxed)""")


class SettlementLine(models.Model):
    _inherit = 'settlement.line'

    def calculate(self, cr, uid, ids, context=None):
        currency_pool = self.pool.get('res.currency')
        line = self.browse(cr, uid, ids, context=context)
        amount = 0
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        # Iterate over the agents and commission in the invoice
        for commission in line.invoice_line_id.commission_ids:
            if commission.agent_id.id == line.settlement_agent_id.agent_id.id:
                commission_app = commission.commission_id  # Get the object
                invoice_line_amount = line.invoice_line_id.price_subtotal
                if commission_app.commission_type == "formula":
                    subtotal = line.invoice_line_id.price_subtotal
                    formula = commission_app.formula.replace(
                        'base', str(subtotal))
                    amount += eval(formula)
                    invoice_currency_id = line.invoice_id.currency_id.id
                    company_currency_id = user.company_id.currency_id.id
                    cc_amount_subtotal = (
                        invoice_currency_id != company_currency_id and
                        currency_pool.compute(
                            cr, uid, invoice_currency_id,
                            company_currency_id,
                            invoice_line_amount,
                            round=False,
                            context=context) or invoice_line_amount)
                    cc_commission_amount = (
                        invoice_currency_id != company_currency_id and
                        currency_pool.compute(
                            cr, uid, invoice_currency_id,
                            company_currency_id,
                            amount,
                            round=False,
                            context=context) or amount)
                    self.write(
                        cr, uid, ids,
                        {
                            'amount': cc_amount_subtotal,
                            'commission_id': commission_app.id,
                            'commission': cc_commission_amount,
                            'currency_id': user.company_id.currency_id.id
                        })
                else:
                    return super(SettlementLine, self).calculate(
                        cr, uid, ids, context=context)


class AgentSettlement(models.Model):
    _inherit = 'settlement.agent'

    def calculate(self, cr, uid, ids, date_from, date_to, context=None):
        settlement_line_pool = self.pool['settlement.line']
        invoice_line_agent_pool = self.pool['invoice.line.agent']
        set_agent = self.browse(cr, uid, ids, context=context)
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        # Recalculate all the line that has commission
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
            # Mark the commission in the invoice as settled
            # and calculate the quantity
            # If we use sections then the quantity is zero,
            # although will reflect the Agent
            if line.commission_id.commission_type == "formula":
                total_per += line.commission
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
            if line.commission_id.commission_type == "fixed":
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
            is_commission_free = product_id.commission_free
            if (line.commission_id.commission_type == "section" and
                    not is_commission_free):
                # We aggregate the base value by grouping
                # by the distinct sections that the agent
                # has assigned for it
                if line.commission_id.id in sections:
                    sections[line.commission_id.id]['base'] = (
                        sections[line.commission_id.id]['base'] +
                        line.invoice_line_id.price_subtotal
                    )
                    # Append the lines for the calculation by sections
                    sections[line.commission_id.id]['lines'].append(line)
                else:
                    sections[line.commission_id.id] = {
                        'type': line.commission_id,
                        'base': line.invoice_line_id.price_subtotal,
                        'lines': [line]
                    }
        # Iterate over each section created
        for tramo in sections:
            # Calculate the commision for each section
            tramo = sections[tramo]
            sections[tramo].update(
                {
                    'commission': tramo['type'].calcula_tramos(tramo['base'])
                }
            )
            total_sections = total_sections + sections[tramo]['commission']
            # Split the commision for each line
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
