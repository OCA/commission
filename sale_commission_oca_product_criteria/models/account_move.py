# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    def _get_line_uom(self):
        return self.object_id.product_uom_id

    def _get_commission_date(self):
        return self.invoice_date or super()._get_commission_date()

    def _get_refunded_commission_item(self, commission):
        """Return the item applied on the line this credit note line refunds.

        The refunded invoice line is the one of the reversed invoice selling
        the same product for the same sale order lines. Without a reversed
        invoice (a return invoiced from the order), the sale order line is the
        closest record of the item that applied.
        """
        refund_line = self.object_id
        origin_lines = self.invoice_id.reversed_entry_id.invoice_line_ids.filtered(
            lambda x: x.product_id == refund_line.product_id
            and x.sale_line_ids == refund_line.sale_line_ids
        )
        agent_lines = origin_lines.agent_ids or refund_line.sale_line_ids.agent_ids
        return agent_lines.filtered(
            lambda x: x.agent_id == self.agent_id and x.commission_id == commission
        ).applied_commission_item_id[:1]

    def _get_commission_item(self, commission, product, quantity=0.0, date=None):
        # A credit note gives back the commission at the item the refunded
        # sale earned, not at the one matching its own date and quantity,
        # the same way it keeps the invoiced price.
        if self.invoice_id.move_type == "out_refund":
            item = self._get_refunded_commission_item(commission)
            if item:
                return item
        return super()._get_commission_item(commission, product, quantity, date)

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
                line._set_applied_commission()
                super(AccountInvoiceLineAgent, line)._compute_amount()
