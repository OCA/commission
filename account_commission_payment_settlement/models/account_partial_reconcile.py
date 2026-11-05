# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    def unlink(self):
        """Every way of undoing an invoice payment (payment return, removing it
        from the invoice, resetting the payment or the invoice to draft) ends here.
        """
        invoices = (self.debit_move_id + self.credit_move_id).move_id.filtered(
            lambda move: move.is_sale_document(include_receipts=True)
        )
        res = super().unlink()
        if invoices:
            self.env["account.invoice.line.agent"].sudo().search(
                [
                    ("invoice_id", "in", invoices.ids),
                    ("settled", "=", True),
                    ("commission_id.invoice_state", "=", "paid"),
                ]
            ).write({"payment_reversal_date": fields.Date.context_today(self)})
        return res
