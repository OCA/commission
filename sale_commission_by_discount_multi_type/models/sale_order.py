from odoo import api, fields, models


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


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

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

    # @api.model
    # def fields_view_get(self, view_id=None, view_type="tree", **kwargs):
    #     if view_type == "tree":
    #         if self._context.get('active_model') == 'sale.order.line':
    #             sol = self.env['sale.order.line'].browse(self._context['active_id'])
    #             view_id = self.env.ref("sale_commission_by_discount_multi_type.view_sale_order_line_tree_multi_type").id
    #         else:
    #             view_id = self.env.ref("sale_commission.view_sale_order_line_tree").id
    #         return super(SaleOrderLineAgent, self).fields_view_get(
    #             view_id=view_id, view_type=view_type, **kwargs
    #         )
    #     return super(SaleOrderLineAgent, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, **kwargs
    #     )
