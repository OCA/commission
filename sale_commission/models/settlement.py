# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io
from itertools import groupby

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form
from odoo.tools import format_date
from odoo.tools.misc import xlsxwriter


class Settlement(models.Model):
    _name = "sale.commission.settlement"
    _description = "Settlement"

    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char("Name")
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
            "res_model": "sale.commission.make.invoice",
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
                line_form.name += "\n" + _("Period: from %s to %s") % (
                    date_from.strftime(lang.date_format),
                    date_to.strftime(lang.date_format),
                )
                line_form.currency_id = (
                    settlement.currency_id
                )  # todo or compute agent currency_id?
                line_form.settlement_id = settlement
                settlement._post_process_line(line_form)
        vals = move_form._values_to_save(all_fields=True)
        return vals

    def _post_process_line(self, line_form):
        pass

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

    def generate_excel_report(self):
        self.ensure_one()

        # Create an in-memory Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        ws = workbook.add_worksheet()

        # Set Excel formatting (optional)
        bold = workbook.add_format({"bold": True})

        # Write header data
        date_from = format_date(self.env, self.date_from)
        date_to = format_date(self.env, self.date_to)

        ws.write(0, 0, "Settlement Report", bold)
        ws.write(2, 0, "Agent", bold)
        ws.write(2, 1, self.agent_id.name)
        ws.write(2, 4, "Company", bold)
        ws.write(2, 5, self.company_id.name)

        ws.write(3, 0, "From", bold)
        ws.write(3, 1, date_from)
        ws.write(3, 4, "To", bold)
        ws.write(3, 5, date_to)

        # Write lines data
        row = 5
        ws.write(row, 0, "Reference Number", bold)
        ws.write(row, 1, "Invoice Date", bold)
        ws.write(row, 2, "Source Invoice Line", bold)
        ws.write(row, 3, "Partner", bold)
        ws.write(row, 4, "Ship To Address", bold)
        ws.write(row, 5, "Commission", bold)
        ws.write(row, 6, "Commission Amount", bold)
        row += 1
        for line in self.line_ids:
            commission_date = format_date(self.env, line.date)
            ws.write(row, 0, line.order_id.name or "")
            ws.write(row, 1, commission_date)
            ws.write(row, 2, line.invoice_line_id.name)
            ws.write(row, 3, line.partner_id.name)
            ws.write(row, 4, line.partner_shipping_id.name or "")
            ws.write(row, 5, line.commission_id.name)
            ws.write(row, 6, line.settled_amount)
            row += 1

        ws.write(row, 5, "Total", bold)
        ws.write(row, 6, self.total, bold)

        # Set column widths
        ws.set_column(0, 1, 15)
        ws.set_column(2, 2, 45)
        ws.set_column(3, 6, 15)
        workbook.close()

        # Get the binary content of the file
        output.seek(0)
        xls_data = output.read()
        output.close()
        encoded_file = base64.b64encode(xls_data)

        # Create an attachment record to store the file
        filename = (
            f"Settlement Report - {self.agent_id.name} "
            f"{self.date_from} to {self.date_to}.xlsx"
        )
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "type": "binary",
                "datas": encoded_file,
                "res_model": "sale.commission.settlement",
                "res_id": self.id,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )

        # Return the download action to the user
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }


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
    order_id = fields.Many2one(
        "sale.order",
        compute="_compute_order_partner_id",
        string="Reference Number",
        store=True,
    )
    partner_id = fields.Many2one(
        "res.partner", compute="_compute_order_partner_id", string="Partner", store=True
    )
    partner_shipping_id = fields.Many2one(
        "res.partner",
        compute="_compute_order_partner_id",
        string="Ship To Address",
        store=True,
    )

    @api.depends(
        "invoice_line_id",
        "invoice_line_id.partner_id",
        "invoice_line_id.sale_line_ids.order_id.partner_id",
        "invoice_line_id.sale_line_ids.order_id.partner_shipping_id",
    )
    def _compute_order_partner_id(self):
        recs = self.filtered("invoice_line_id")
        for rec in recs:
            rec.order_id = rec.invoice_line_id.sale_line_ids.order_id.id
            rec.partner_id = (
                rec.order_id.partner_id.id or rec.invoice_line_id.partner_id.id
            )
            rec.partner_shipping_id = rec.order_id.partner_shipping_id.id
        (self - recs).update(
            dict(order_id=False, partner_id=False, partner_shipping_id=False)
        )

    @api.constrains("settlement_id", "agent_line")
    def _check_company(self):
        for record in self:
            for line in record.agent_line:
                if line.company_id != record.company_id:
                    raise UserError(_("Company must be the same"))
