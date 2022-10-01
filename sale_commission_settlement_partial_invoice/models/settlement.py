#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.float_utils import float_compare, float_is_zero


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"

    invoiced_amount = fields.Float(
        compute="_compute_state", store=True, readonly=True)
    invoice_count = fields.Integer(
        string="Invoice Count", compute="_compute_state", store=True,
        readonly=True)
    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        compute="_compute_invoice_ids",
        store=True,
    )
    invoice_line_ids = fields.Many2many(
        comodel_name="account.invoice.line",
        string="Generated invoice lines",
        readonly=True,
    )
    state = fields.Selection(compute="_compute_state", store=True)

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_invoice_ids(self):
        for settlement in self:
            invoice_lines = settlement.invoice_line_ids
            settlement.invoice_ids = invoice_lines.mapped('invoice_id')

    @api.multi
    @api.depends(
        "currency_id.rounding",
        "invoice_ids",
        "invoice_line_ids.price_subtotal",
        "total",
    )
    def _compute_state(self):
        for settlement in self:
            if not settlement.total:
                settlement.state = "settled"
                return
            settlement.invoice_count = len(settlement.invoice_ids)

            invoiced_amount = 0
            for inv_line in settlement.invoice_line_ids:
                invoiced_amount += inv_line.price_subtotal
            settlement.invoiced_amount = invoiced_amount

            if float_compare(
                settlement.total, settlement.invoiced_amount,
                precision_rounding=settlement.currency_id.rounding
            ) > 0:
                settlement.state = "settled"
            else:
                settlement.state = "invoiced"

    @api.multi
    def make_invoices(self, journal, product, date=False):
        res = super(Settlement, self).make_invoices(journal, product, date)
        for settlement in self:
            invoice = settlement.invoice
            settlement.invoice_line_ids = [
                (4, line_id)
                for line_id in invoice.invoice_line_ids.ids
            ]
        return res

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped("invoice_ids")
        action = self.env.ref("account.action_vendor_bill_template").read()[0]
        if len(invoices) > 1:
            action["domain"] = [("id", "in", invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref("account.invoice_supplier_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = invoices.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def _prepare_invoice_line(self, settlement, invoice, product):
        """Remove already invoiced amount from new invoice lines"""
        invoice_line_vals = super(Settlement, self)._prepare_invoice_line(
            settlement, invoice, product)
        settlement_invoiced_amount = settlement.invoiced_amount
        if not float_is_zero(
            settlement_invoiced_amount,
            precision_rounding=settlement.currency_id.rounding,
        ):
            if invoice.type == "in_refund":
                invoice_line_vals["price_unit"] += settlement_invoiced_amount
            else:
                invoice_line_vals["price_unit"] -= settlement_invoiced_amount
        return invoice_line_vals
