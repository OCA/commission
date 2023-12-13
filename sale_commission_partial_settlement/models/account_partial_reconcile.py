from odoo import fields, models


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    partial_commission_settled = fields.Boolean()

    def _skip_future_partial_payments(self, date_payment_to, counterpart_line_date):
        if date_payment_to and date_payment_to < counterpart_line_date:
            return True
        return False
