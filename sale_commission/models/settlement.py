# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _


class Settlement(models.Model):
    _name = "sale.commission.settlement"
    _rec_name = "agent"

    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    total = fields.Float(compute="_compute_total", readonly=True, store=True)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    agent = fields.Many2one(
        comodel_name="res.partner", domain="[('agent', '=', True)]")
    agent_type = fields.Selection(related='agent.agent_type')
    lines = fields.One2many(
        comodel_name="sale.commission.settlement.line",
        inverse_name="settlement", string="Settlement lines", readonly=True)
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
    company_id = fields.Many2one('res.company', 'Company')

    @api.depends('lines', 'lines.settled_amount')
    def _compute_total(self):
        for record in self:
            record.total = sum(x.settled_amount for x in record.lines)

    @api.multi
    def action_cancel(self):
        if any(x.state != 'settled' for x in self):
            raise exceptions.Warning(
                _('Cannot cancel an invoiced settlement.'))
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        """Allow to delete only cancelled settlements"""
        if any(x.state == 'invoiced' for x in self):
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
            'type': ('in_invoice' if journal.type == 'purchase' else
                     'in_refund'),
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
        lang = self.env['res.lang'].search(
            [('code', '=', partner.lang or self.env.context.get('lang',
                                                                'en_US'))])
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
    def make_invoices(self, journal, refund_journal, product, date=False):
        invoice_obj = self.env['account.invoice']
        for settlement in self:
            # select the proper journal according to settlement's amount
            # considering _add_extra_invoice_lines sum of values
            extra_invoice_lines = self._add_extra_invoice_lines(settlement)
            extra_total = sum(x['price_unit'] for x in extra_invoice_lines)
            invoice_journal = (journal if
                               (settlement.total + extra_total) >= 0 else
                               refund_journal)
            invoice_vals = self._prepare_invoice_header(
                settlement, invoice_journal, date=date)
            invoice_lines_vals = []
            invoice_lines_vals.append(self._prepare_invoice_line(
                settlement, invoice_vals, product))
            invoice_lines_vals += extra_invoice_lines
            # invert invoice values if it's a refund
            if invoice_vals['type'] == 'in_refund':
                for line in invoice_lines_vals:
                    line['price_unit'] = -line['price_unit']
            invoice_vals['invoice_line'] = [(0, 0, x)
                                            for x in invoice_lines_vals]
            invoice = invoice_obj.create(invoice_vals)
            settlement.state = 'invoiced'
            settlement.invoice = invoice.id


class SettlementLine(models.Model):
    _name = "sale.commission.settlement.line"

    settlement = fields.Many2one(
        "sale.commission.settlement", readonly=True, ondelete="cascade",
        required=True)
    agent_line = fields.Many2many(
        comodel_name='account.invoice.line.agent',
        relation='settlement_agent_line_rel', column1='settlement_id',
        column2='agent_line_id', required=True)
    date = fields.Date(related="agent_line.invoice_date", store=True)
    invoice_line = fields.Many2one(
        comodel_name='account.invoice.line', store=True,
        related='agent_line.invoice_line')
    invoice = fields.Many2one(
        comodel_name='account.invoice', store=True, string="Invoice",
        related='invoice_line.invoice_id')
    agent = fields.Many2one(
        comodel_name="res.partner", readonly=True, related="agent_line.agent",
        store=True)
    settled_amount = fields.Float(
        related="agent_line.amount", readonly=True, store=True)
    commission = fields.Many2one(
        comodel_name="sale.commission", related="agent_line.commission")
    company_id = fields.Many2one('res.company', 'Company',
                                 related="settlement.company_id", store=True)
