from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"

    def select_suitable_commission_item(self, item_ids, product):
        discount = self.object_id.discount
        # Check discount condition
        commission_item = False
        for item_id in item_ids:
            commission_item = self.env["commission.item"].browse(item_id)
            # If both is 0 then discount condition check is disabled
            if commission_item.discount_from + commission_item.discount_to > 0:
                if (
                    commission_item.discount_from
                    <= discount
                    < commission_item.discount_to
                ):
                    break
            else:
                break
            commission_item = False
        return commission_item


class CommissionItem(models.Model):
    _inherit = "commission.item"

    discount_from = fields.Float("Discount From")
    discount_to = fields.Float("Discount To")

    @api.constrains("discount_from", "discount_to")
    def _check_discounts(self):
        if any(item.discount_from > item.discount_to for item in self):
            raise ValidationError(
                _("Discount From should be lower than the Discount To.")
            )
        return True
