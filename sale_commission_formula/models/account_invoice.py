# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class AccountInvoiceLineAgent(models.Model):
    _inherit = 'account.invoice.line.agent'

    def _compute_amount(self):
        """Invert sign of refund invoices computed by formula."""
        super()._compute_amount()
        applicable_lines = self.filtered(lambda x: (
            not x.source_product_id.commission_free and x.commission
            and x.commission.commission_type == 'formula'
            and x.invoice.type in ('out_refund', 'in_refund')
        ))
        for line in applicable_lines:
            line.amount = -line.amount
