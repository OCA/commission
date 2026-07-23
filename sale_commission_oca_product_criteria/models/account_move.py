# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    applied_commission_item_id = fields.Many2one("commission.item")

    def _get_line_uom(self):
        return self.object_id.product_uom_id

    def _get_commission_date(self):
        return self.invoice_date or super()._get_commission_date()

    @api.depends(
        "object_id.price_subtotal",
        "object_id.product_id.commission_free",
        "object_id.quantity",
        "object_id.product_uom_id",
        "object_id.currency_id",
        "commission_id",
        "invoice_date",
    )
    def _compute_amount(self):  # pylint: disable=W8110 # Computes don't return
        for line in self:
            if line.commission_id and line.commission_id.commission_type == "product":
                inv_line = line.object_id
                line.amount = line._get_single_commission_amount(
                    line.commission_id,
                    inv_line.price_subtotal,
                    inv_line.product_id,
                    inv_line.quantity,
                )
                # Refunds commissions are negative
                if line.invoice_id.move_type and "refund" in line.invoice_id.move_type:
                    line.amount = -line.amount
            else:
                super(AccountInvoiceLineAgent, line)._compute_amount()
