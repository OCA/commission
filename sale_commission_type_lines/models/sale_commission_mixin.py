from odoo import models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        # method replaced
        self.ensure_one()
        if (
            commission.commission_type != "cat_prod_var"
            or self._name == "account.invoice.line.agent"
        ):
            return super(SaleCommissionLineMixin, self)._get_commission_amount(
                commission, subtotal, product, quantity
            )
        if product.commission_free or not commission:
            return 0.0
        item_ids = self._get_commission_items(commission, product)
        commission_item = self.select_suitable_commission_item(item_ids, product)
        if not commission_item:
            return 0.0
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        self.applied_commission_item_id = commission_item
        if commission_item.commission_type == "fixed":
            return commission_item.fixed_amount
        elif commission_item.commission_type == "percentage":
            return subtotal * (commission_item.percent_amount / 100.0)

    def select_suitable_commission_item(self, item_ids, product):
        # inherit it
        if len(item_ids) < 1:
            return False
        commission_item = self.env["commission.item"].browse(item_ids[0])
        return commission_item

    def _get_commission_items(self, commission, product):
        categ_ids = {}
        categ = product.categ_id
        while categ:
            categ_ids[categ.id] = True
            categ = categ.parent_id
        categ_ids = list(categ_ids)
        # Select all suitable items. Order by best match
        # (priority is: all/cat/subcat/product/variant).
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                commission_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.commission_id = %s)
            ORDER BY
                item.applied_on, categ.complete_name desc, item.id desc
            """,
            (product.product_tmpl_id.ids, product.ids, categ_ids, commission.id),
        )
        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return item_ids
