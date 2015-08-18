# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#    Copyright (C) 2015 Avanzosc (<http://www.avanzosc.es>)
#    Copyright (C) 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
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

from openerp import models, fields, api, exceptions, tools, _


class Settlement(models.Model):
    _name = "sale.commission.settlement"

    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    total = fields.Float(compute="_get_total", readonly=True, store=True)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    agent = fields.Many2one(
        comodel_name="res.partner", domain="[('agent', '=', True)]")
    agent_type = fields.Selection(related='agent.agent_type')
    lines = fields.One2many(
        comodel_name="account.invoice.line.commission",
        inverse_name="settlement_id", string="Settlement lines", readonly=True)
    state = fields.Selection(
        selection=[("settled", "Settled"),
                   ("invoiced", "Invoiced"),
                   ("cancel", "Canceled"),
                   ("except_invoice", "Invoice exception")], string="State",
        readonly=True, default="settled")
    invoice = fields.Many2one(
        comodel_name="account.invoice", string="Generated invoice",
        readonly=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', readonly=True,
        default=_default_currency)

    @api.one
    @api.depends('lines', 'lines.amount')
    def _get_total(self):
        self.total = sum(x.amount for x in self.lines)

    @api.multi
    def action_cancel(self):
        if any(x.state != 'settled' for x in self):
            raise exceptions.Warning(
                _('Cannot cancel an invoiced settlement.'))
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        """Allow to delete only cancelled settlements"""
        if any(x.state != 'cancel' for x in self):
            raise exceptions.Warning(
                _("You can't delete invoiced settlements."))
        return super(Settlement, self).unlink()

    @api.multi
    def action_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Make invoice'),
            'res_model': 'sale.commission.make.invoice',
            'view_type': 'form',
            'target': 'new',
            'view_mode': 'form',
            'context': {'settlement_ids': self.ids}
        }

    def _prepare_invoice_header(self, settlement, journal, date=False):
        invoice_obj = self.env['account.invoice']
        invoice_vals = {
            'partner_id': settlement.agent.id,
            'type': 'in_invoice',
            'date_invoice': date,
            'journal_id': journal.id,
            'company_id': self.env.user.company_id.id,
            'state': 'draft',
        }
        # Get other invoice values from partner onchange
        invoice_vals.update(invoice_obj.onchange_partner_id(
            type=invoice_vals['type'],
            partner_id=invoice_vals['partner_id'],
            company_id=invoice_vals['company_id'])['value'])
        return invoice_vals

    def _prepare_invoice_line(self, settlement, invoice_vals, product):
        invoice_line_obj = self.env['account.invoice.line']
        invoice_line_vals = {
            'product_id': product.id,
            'quantity': 1,
        }
        # Get other invoice line values from product onchange
        invoice_line_vals.update(invoice_line_obj.product_id_change(
            product=invoice_line_vals['product_id'], uom_id=False,
            type=invoice_vals['type'], qty=invoice_line_vals['quantity'],
            partner_id=invoice_vals['partner_id'],
            fposition_id=invoice_vals['fiscal_position'])['value'])
        # Put line taxes
        invoice_line_vals['invoice_line_tax_id'] = \
            [(6, 0, tuple(invoice_line_vals['invoice_line_tax_id']))]
        # Put commission fee
        invoice_line_vals['price_unit'] = settlement.total
        # Put period string
        partner = self.env['res.partner'].browse(invoice_vals['partner_id'])
        lang = self.env['res.lang'].search([('code', '=', partner.lang)])
        date_from = fields.Date.from_string(settlement.date_from)
        date_to = fields.Date.from_string(settlement.date_to)
        invoice_line_vals['name'] += "\n" + _('Period: from %s to %s') % (
            date_from.strftime(lang.date_format),
            date_to.strftime(lang.date_format))
        return invoice_line_vals

    def _add_extra_invoice_lines(self, settlement):
        """Hook for adding extra invoice lines.
        :param settlement: Source settlement.
        :return: List of dictionaries with the extra lines.
        """
        return []

    @api.multi
    def make_invoices(self, journal, product, date=False):
        invoice_obj = self.env['account.invoice']
        for settlement in self:
            invoice_vals = self._prepare_invoice_header(
                settlement, journal, date=date)
            invoice_lines_vals = []
            invoice_lines_vals.append(self._prepare_invoice_line(
                settlement, invoice_vals, product))
            invoice_lines_vals += self._add_extra_invoice_lines(settlement)
            invoice_vals['invoice_line'] = [(0, 0, x)
                                            for x in invoice_lines_vals]
            invoice = invoice_obj.create(invoice_vals)
            settlement.state = 'invoiced'
            settlement.invoice = invoice.id


class SettlementLine(models.Model):
    _name = "sale.commission.settlement.line"
    _auto = False

    settlement = fields.Many2one("sale.commission.settlement",
                                 readonly=True)
    date = fields.Date(readonly=True)
    invoice_line = fields.Many2one(comodel_name='account.invoice.line',
                                   readonly=True)
    invoice = fields.Many2one(comodel_name='account.invoice',
                              string="Invoice", readonly=True)
    agent = fields.Many2one(comodel_name="res.partner", readonly=True)
    settled_amount = fields.Float(readonly=True)
    commission = fields.Many2one(comodel_name="sale.commission",
                                 readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """
            CREATE OR REPLACE VIEW {table} AS (
                SELECT comm_line.id             AS id
                     , settlement.id            AS settlement
                     , comm_line.invoice_date   AS date
                     , comm_line.invoice_line   AS invoice_line
                     , comm_line.invoice        AS invoice_id
                     , comm_line.agent          AS agent
                     , comm_line.amount         AS settled_amount
                     , comm_line.commission     AS commission
                FROM sale_commission_settlement settlement
                INNER JOIN account_invoice_line_commission comm_line
                        ON settlement.id = comm_line.settlement_id
            )
            """.format(
                table=self._table,
            ),
        )
