# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form


class Settlement(models.Model):
    _name = "sale.commission.settlement"
    _description = "Settlement"

    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    @api.depends('agent_id', 'date_from', 'date_to')
    def _compute_name(self):
        for settlement in self:
            lang = self.env["res.lang"].search(
                [("code", "=", settlement.agent_id.lang or self.env.context.get("lang", "en_US"))]
            )
            settlement.name = "%s: %s" % (settlement.agent_id.display_name, _("Period: from %s to %s") % (
                settlement.date_from.strftime(lang.date_format),
                settlement.date_to.strftime(lang.date_format),
            ))

    name = fields.Char("Name", compute='_compute_name', store=True)
    total = fields.Float(compute="_compute_total", readonly=True, store=True)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    agent_id = fields.Many2one(
        comodel_name="res.partner", domain="[('agent', '=', True)]"
    )
    agent_type = fields.Selection(related="agent_id.agent_type")
    line_ids = fields.One2many(
        comodel_name="sale.commission.settlement.line",
        inverse_name="settlement_id",
        string="Settlement lines",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("settled", "Settled"),
            ("invoiced", "Invoiced"),
            ("cancel", "Canceled"),
            ("except_invoice", "Invoice exception"),
        ],
        string="State",
        readonly=True,
        default="settled",
    )
    invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="settlement_id",
        string="Generated invoice",
        readonly=True,
    )
    # TODO: To be removed
    invoice_id = fields.Many2one(
        store=True,
        comodel_name="account.move",
        compute="_compute_invoice_id",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", readonly=True, default=_default_currency
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )

    @api.depends("line_ids", "line_ids.settled_amount")
    def _compute_total(self):
        for record in self:
            record.total = sum(record.mapped("line_ids.settled_amount"))

    @api.depends("invoice_ids")
    def _compute_invoice_id(self):
        for record in self:
            record.invoice_id = record.invoice_ids[:1]

    def action_cancel(self):
        if any(x.state != "settled" for x in self):
            raise UserError(_("Cannot cancel an invoiced settlement."))
        self.write({"state": "cancel"})

    def unlink(self):
        """Allow to delete only cancelled settlements"""
        if any(x.state == "invoiced" for x in self):
            raise UserError(_("You can't delete invoiced settlements."))
        return super().unlink()

    def action_invoice(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Make invoice"),
            "res_model": "sale.commission.make.invoice",
            "view_type": "form",
            "target": "new",
            "view_mode": "form",
            "context": {"settlement_ids": self.ids},
        }

    def _prepare_invoice_lines(self, move_form, product, detailed_invoice):
        self.ensure_one()
        partner = self.agent_id
        lang = self.env["res.lang"].search(
            [("code", "=", partner.lang or self.env.context.get("lang", "en_US"))]
        )
        date_from = fields.Date.from_string(self.date_from)
        date_to = fields.Date.from_string(self.date_to)
        if detailed_invoice == 'no_details':
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = product
                line_form.quantity = 1
                line_form.price_unit = abs(self.total)
                line_form.name += "\n" + _("Period: from %s to %s") % (
                    date_from.strftime(lang.date_format),
                    date_to.strftime(lang.date_format),
                )
                line_form.currency_id = (
                    self.currency_id
                )  # todo or compute agent currency_id?
        elif detailed_invoice == 'line_details':
            for line in self.line_ids:
                with move_form.invoice_line_ids.new() as line_form:
                    line_form.product_id = product
                    line_form.quantity = 1
                    line_form.price_unit = line.settled_amount
                    line_form.name = "%s: %s\n%s" % (
                        line.invoice_line_id.move_id.name,
                        line.invoice_line_id.name,
                        _("Period: from %s to %s") % (
                            date_from.strftime(lang.date_format),
                            date_to.strftime(lang.date_format),
                        )
                    )
                    line_form.currency_id = (
                        self.currency_id
                    )  # todo or compute agent currency_id?
        elif detailed_invoice == 'invoice_details':
            invoices = {}
            for line in self.line_ids:
                if line.invoice_line_id.move_id.id not in invoices:
                    invoices[line.invoice_line_id.move_id.id] = {
                        'invoice': line.invoice_line_id.move_id,
                        'amount': 0.0,
                    }
                invoices[line.invoice_line_id.move_id.id]['amount'] += line.settled_amount
            for invoice_id in invoices:
                invoice = invoices[invoice_id]
                with move_form.invoice_line_ids.new() as line_form:
                    line_form.product_id = product
                    line_form.quantity = 1
                    line_form.price_unit = invoice['amount']
                    line_form.name = "%s: %s" % (
                        invoice['invoice'].name,
                        _("Period: from %s to %s") % (
                            date_from.strftime(lang.date_format),
                            date_to.strftime(lang.date_format),
                        )
                    )
                    line_form.currency_id = (
                        self.currency_id
                    )  # todo or compute agent currency_id?

    def _prepare_invoice(self, journal, product, date=False, detailed_invoice=False):
        self.ensure_one()
        move_type = "in_invoice" if self.total >= 0 else "in_refund"
        move_form = Form(
            self.env["account.move"].with_context(default_move_type=move_type)
        )
        if date:
            move_form.invoice_date = date
        move_form.partner_id = self.agent_id
        move_form.journal_id = journal
        self._prepare_invoice_lines(move_form, product, detailed_invoice)
        vals = move_form._values_to_save(all_fields=True)
        vals["settlement_id"] = self.id
        return vals

    def make_invoices(self, journal, product, date=False, detailed_invoice='no_details'):
        invoice_vals_list = []
        for settlement in self:
            invoice_vals = settlement._prepare_invoice(journal, product, date, detailed_invoice)
            invoice_vals_list.append(invoice_vals)
        invoices = self.env["account.move"].create(invoice_vals_list)
        self.write({"state": "invoiced"})
        return invoices


class SettlementLine(models.Model):
    _name = "sale.commission.settlement.line"
    _description = "Line of a commission settlement"

    settlement_id = fields.Many2one(
        "sale.commission.settlement", readonly=True, ondelete="cascade", required=True
    )
    agent_line = fields.Many2many(
        comodel_name="account.invoice.line.agent",
        relation="settlement_agent_line_rel",
        column1="settlement_id",
        column2="agent_line_id",
        required=True,
    )
    date = fields.Date(related="agent_line.invoice_date", store=True)
    invoice_line_id = fields.Many2one(
        comodel_name="account.move.line",
        store=True,
        related="agent_line.object_id",
        string="Source invoice line",
    )
    agent_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
        related="agent_line.agent_id",
        store=True,
    )
    settled_amount = fields.Monetary(
        related="agent_line.amount", readonly=True, store=True
    )
    currency_id = fields.Many2one(
        related="agent_line.currency_id",
        store=True,
        readonly=True,
    )
    commission_id = fields.Many2one(
        comodel_name="sale.commission", related="agent_line.commission_id"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="settlement_id.company_id",
    )

    @api.constrains("settlement_id", "agent_line")
    def _check_company(self):
        for record in self:
            for line in record.agent_line:
                if line.company_id != record.company_id:
                    raise UserError(_("Company must be the same"))
