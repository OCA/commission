from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    product_domain_ids = fields.Many2many("product.product", string="Products Domain")

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        product_ids = self.env["product.product"]
        if self.partner_id:
            for item in self.partner_id.commission_item_agent_ids:
                commission = item.agent_id.commission_id
                if commission:
                    product_ids = self._get_products_from_commission(commission, item)
        self.product_domain_ids = product_ids or product_ids.search([])

    @api.model
    def _get_products_from_commission(self, commission, item):
        product_ids = self.env["product.product"]
        for rule in commission.item_ids.filtered(
            lambda x: x.group_id in item.group_ids
        ):
            if rule.applied_on == "3_global":
                product_ids = self.env["product.product"].search([])
                break
            elif rule.applied_on == "2_product_category":
                product_ids |= self.env["product.product"].search(
                    [("product_tmpl_id.categ_id", "=", rule.categ_id.id)]
                )
            elif rule.applied_on == "1_product":
                product_ids |= self.env["product.product"].search(
                    [("product_tmpl_id", "=", rule.product_tmpl_id.id)]
                )
            elif rule.applied_on == "0_product_variant":
                product_ids |= rule.product_id
        return product_ids
