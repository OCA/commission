from odoo import models, fields, api
from odoo.tools.float_utils import float_compare


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"

    invoiced_amount = fields.Float(
        compute="_compute_state", store=True, readonly=True)
    invoice_count = fields.Integer(
        string="Invoice Count", compute="_compute_state", store=True,
        readonly=True)
    invoice_ids = fields.Many2many(
        "account.invoice", string="Generated invoices", readonly=True)
    state = fields.Selection(compute="_compute_state", store=True)

    @api.depends("invoice_ids.amount_untaxed")
    def _compute_state(self):
        for settlement in self:
            if not settlement.total:
                settlement.state = "settled"
                return
            settlement.invoice_count = len(settlement.invoice_ids)
            settlement.invoiced_amount = 0
            for inv in settlement.invoice_ids:
                settlement.invoiced_amount += inv.amount_untaxed
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
            settlement.invoice_ids = [(4, settlement.invoice.id)]
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
        invoice_line_vals = super(Settlement, self)._prepare_invoice_line(
            settlement, invoice, product)
        if settlement.invoice_ids:
            invoices_amount = sum(settlement.invoice_ids.mapped("amount_untaxed"))
            if invoice.type == "in_refund":
                invoice_line_vals["price_unit"] += invoices_amount
            else:
                invoice_line_vals["price_unit"] -= invoices_amount
        return invoice_line_vals
