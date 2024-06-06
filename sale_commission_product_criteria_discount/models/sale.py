# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    discount_from = fields.Float(related="applied_commission_item_id.discount_from")
    discount_to = fields.Float(related="applied_commission_item_id.discount_to")

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        # Replaced to add pricelist condition. Original in sale.commission.line.mixin.
        self.ensure_one()
        if product.commission_free or not commission:
            return 0.0
        if commission.commission_type in ["percentage", "fixed"]:
            return self._get_commission_amount(commission, subtotal, product, quantity)
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return 0.0
        # Check discount condition
        item_ids = self.env["commission.item"].browse(item_ids)
        commission_item = False
        for item_id in item_ids:
            commission_item = item_id
            discount = self._get_discount_value(commission_item)
            if commission_item.based_on != "sol":
                if (
                    commission_item.discount_from
                    <= discount
                    <= commission_item.discount_to
                ):
                    break  # suitable item found
            else:
                break  # suitable item found
            commission_item = False
        if not commission_item:
            # all commission items rejected
            return 0.0
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        self.applied_commission_item_id = commission_item
        # if self.agent_id.use_multi_type_commissions:
        self.applied_commission_id = commission_item.commission_id
        if commission_item.commission_type == "fixed":
            return commission_item.fixed_amount
        elif commission_item.commission_type == "percentage":
            return subtotal * (commission_item.percent_amount / 100.0)
