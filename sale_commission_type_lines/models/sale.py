# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    display_agent_icon = fields.Boolean(compute="_compute_display_agent_icon")

    def _compute_display_agent_icon(self):
        param = self.env.company.display_invoiced_agent_icon
        for r in self:
            r.display_agent_icon = param or not (
                not param and r.invoice_status == "invoiced"
            )


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    discount = fields.Float(related="object_id.discount")
    applied_commission_item_id = fields.Many2one("commission.item")
    based_on = fields.Selection(related="applied_commission_item_id.based_on")
    applied_on_name = fields.Char(related="applied_commission_item_id.name")
    discount_from = fields.Float(related="applied_commission_item_id.discount_from")
    discount_to = fields.Float(related="applied_commission_item_id.discount_to")
    commission_type = fields.Selection(
        related="applied_commission_item_id.commission_type"
    )
    fixed_amount = fields.Float(related="applied_commission_item_id.fixed_amount")
    percent_amount = fields.Float(related="applied_commission_item_id.percent_amount")
    use_multi_type_commissions = fields.Boolean(
        related="agent_id.use_multi_type_commissions"
    )

    @api.depends(
        "object_id.price_subtotal", "object_id.product_id", "object_id.product_uom_qty"
    )
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                line.commission_ids,
                order_line.price_subtotal,
                order_line.product_id,
                order_line.product_uom_qty,
            )

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        # Replaced to add pricelist condition. Original in sale.commission.line.mixin.
        self.ensure_one()
        if product.commission_free or not commission:
            return 0.0
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return 0.0
        so_id = self.object_id.order_id
        # Check discount condition
        commission_item = False
        for item_id in item_ids:
            commission_item = self.env["commission.item"].browse(item_id)
            discount = self._get_discount_value(commission_item)
            if commission_item.based_on != "sol":
                if (
                    commission_item.discount_from
                    <= discount
                    <= commission_item.discount_to
                ):
                    break  # suitable item found
            else:
                if (
                    commission_item.pricelist_id
                    and so_id.pricelist_id.id != commission_item.pricelist_id.id
                ):
                    commission_item = False  # unsuitable item
                else:
                    break  # suitable item found
            commission_item = False
        if not commission_item:
            # all commission items was rejected
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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals["agent_ids"] = [
            (
                0,
                0,
                {
                    "agent_id": x.agent_id.id,
                    "commission_id": x.commission_id.id,
                    "commission_ids": x.commission_ids.ids,
                },
            )
            for x in self.agent_ids
        ]
        return vals
