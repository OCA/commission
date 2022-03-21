# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        """Get the commission amount for the data given. To be called by
        compute methods of children models.
        """
        self.ensure_one()
        if (
            not product.commission_free
            and commission
            and commission.commission_type == "supplierinfo"
        ):
            params = {}
            date = None
            uom_id = None
            if self.object_id._name == "sale.order.line":
                params = {"sale_order_line": self.object_id}
                uom_id = self.object_id.product_uom
                date = (
                    self.object_id.order_id.date_order
                    and self.object_id.order_id.date_order.date()
                )
            elif self.object_id._name == "account.move.line":
                params = {"account_move_line": self.object_id}
                uom_id = self.object_id.product_uom_id
                date = (
                    self.object_id.sale_line_ids.order_id.date_order
                    or self.object_id.move_id.date
                    or fields.Date.today()
                )
            seller = product._select_seller(
                partner_id=self.agent_id,
                quantity=self.amount,
                date=date,
                uom_id=uom_id,
                params=params,
            )
            return (seller.price or product.standard_price) * quantity
        return super()._get_commission_amount(commission, subtotal, product, quantity)
