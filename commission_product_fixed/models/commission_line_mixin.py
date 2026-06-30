# Copyright 2026 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        """Compute the commission as a fixed amount per product unit.

        The sale price, discount and margin are not taken into account: the
        amount is the per-product fixed value (which differs by agent, as each
        agent points to its own commission) multiplied by the quantity.
        """
        self.ensure_one()
        if commission and commission.commission_type == "product_fixed":
            if product.commission_free:
                return 0.0
            date = getattr(self, "invoice_date", False) or (
                fields.Date.context_today(self)
            )
            line = commission._get_product_fixed_line(product, date, quantity)
            if not line:
                # Missing configuration. The amount is left at 0 here and the
                # posting of the invoice is blocked in account.move to force a
                # proper setup (see _check_product_fixed_commission).
                return 0.0
            amount = line.amount * quantity
            if (
                line.currency_id
                and self.currency_id
                and (line.currency_id != self.currency_id)
            ):
                company = getattr(self, "company_id", False) or self.env.company
                amount = line.currency_id._convert(
                    amount, self.currency_id, company, date
                )
            return amount
        return super()._get_commission_amount(commission, subtotal, product, quantity)
