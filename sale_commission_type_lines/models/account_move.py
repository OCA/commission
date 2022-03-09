from odoo import fields, models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    applied_commission_item_id = fields.Many2one("commission.item")

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        so = self.env["sale.order"].search([("invoice_ids", "in", self.invoice_id.ids)])
        if so:
            # required when using down payment invoice (fixed or percent).
            commission_part = self.invoice_id.amount_total / so.amount_total
            invoice_commission = commission_part * so.commission_total
            return invoice_commission
        return 0.0
