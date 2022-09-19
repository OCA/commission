# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form


class Settlement(models.Model):
    _name = "commission.settlement"
    _description = "Settlement"

    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char()
    total = fields.Float(compute="_compute_total", readonly=True, store=True)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    agent_id = fields.Many2one(
        comodel_name="res.partner", domain="[('agent', '=', True)]"
    )
    agent_type = fields.Selection(related="agent_id.agent_type")
    settlement_type = fields.Char(
        readonly=True,
        help="e.g. 'invoice'. A technical field to control the view presentation.",
    )
    line_ids = fields.One2many(
        comodel_name="commission.settlement.line",
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
        readonly=True,
        default="settled",
    )
    invoice_line_ids = fields.One2many(
        comodel_name="account.move.line",
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

    @api.depends("invoice_line_ids")
    def _compute_invoice_id(self):
        for record in self:
            record.invoice_id = record.invoice_line_ids[:1].move_id

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
            "res_model": "commission.make.invoice",
            "view_type": "form",
            "target": "new",
            "view_mode": "form",
            "context": {"settlement_ids": self.ids},
        }

    def _get_invoice_partner(self):
        return self[0].agent_id

    def _prepare_invoice(self, journal, product, date=False):

        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )

        if date:
            move_form.invoice_date = date
        partner = self._get_invoice_partner()
        move_form.partner_id = partner
        move_form.journal_id = journal
        for settlement in self:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = product
                line_form.quantity = -1 if settlement.total < 0 else 1
                line_form.price_unit = abs(settlement.total)
                # Put period string
                partner = self.agent_id
                lang = self.env["res.lang"].search(
                    [
                        (
                            "code",
                            "=",
                            partner.lang or self.env.context.get("lang", "en_US"),
                        )
                    ]
                )
                date_from = fields.Date.from_string(settlement.date_from)
                date_to = fields.Date.from_string(settlement.date_to)
                line_form.name += "\n" + _(
                    "Period: from %(date_from)s to %(date_to)s",
                    date_from=date_from.strftime(lang.date_format),
                    date_to=date_to.strftime(lang.date_format),
                )
                line_form.currency_id = (
                    settlement.currency_id
                )  # todo or compute agent currency_id?\
                line_form.settlement_id = settlement
        vals = move_form._values_to_save(all_fields=True)
        return vals

    def _get_invoice_grouping_keys(self):
        return ["company_id", "agent_id"]

    def make_invoices(self, journal, product, date=False, grouped=False):
        invoice_vals_list = []
        settlement_obj = self.env[self._name]
        if grouped:
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            settlements = groupby(
                self.sorted(
                    key=lambda x: [
                        x._fields[grouping_key].convert_to_write(x[grouping_key], x)
                        for grouping_key in invoice_grouping_keys
                    ],
                ),
                key=lambda x: [
                    x._fields[grouping_key].convert_to_write(x[grouping_key], x)
                    for grouping_key in invoice_grouping_keys
                ],
            )
            grouped_settlements = [
                settlement_obj.union(*list(sett))
                for _grouping_keys, sett in settlements
            ]
        else:
            grouped_settlements = self
        for settlement in grouped_settlements:
            invoice_vals = settlement._prepare_invoice(journal, product, date)
            invoice_vals_list.append(invoice_vals)
        invoices = self.env["account.move"].create(invoice_vals_list)
        invoices.sudo().filtered(lambda m: m.amount_total < 0).with_context(
            include_settlement=True
        ).action_switch_invoice_into_refund_credit_note()
        self.write({"state": "invoiced"})
        return invoices


class SettlementLine(models.Model):
    _name = "commission.settlement.line"
    _description = "Line of a commission settlement"

    settlement_id = fields.Many2one(
        "commission.settlement",
        readonly=True,
        ondelete="cascade",
        required=True,
    )

    date = fields.Date()
    agent_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
        store=True,
    )
    settled_amount = fields.Monetary(readonly=True, store=True)
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        store=True,
        readonly=True,
    )
    commission_id = fields.Many2one(
        comodel_name="commission",
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="settlement_id.company_id",
    )
