from odoo import fields, models


class SaleCommissionMixin(models.AbstractModel):
    _inherit = "sale.commission.mixin"

    def _prepare_agent_vals(self, agent):
        return {"agent_id": agent.id, "commission_id": agent.commission_id.id, "commission_ids": agent.commission_ids.ids}


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"

    commission_ids = fields.Many2many("sale.commission")

    def _get_commission_amount(self, commission, commissions, subtotal, product, quantity):
        # Method replaced
        if commissions:
            return self._get_multi_commission_amount(commissions, subtotal, product, quantity)
        elif commission:
            return self._get_single_commission_amount(commission, subtotal, product, quantity)

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
            (product.product_tmpl_id.ids, product.ids, categ_ids, commission._origin.id),
        )
        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return item_ids

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        if commission.commission_type != "cat_prod_var":
            return super(SaleCommissionLineMixin, self)._get_commission_amount(
                commission, subtotal, product, quantity
            )
        self.ensure_one()
        discount = self.object_id.discount
        if product.commission_free or not commission:
            return 0.0
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return 0.0
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
        if not commission_item:
            # all commission items was rejected because of discount condition
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

    def _get_multi_commission_amount(self, commissions, subtotal, product, quantity):
        res = []
        for com in commissions:
            res.append(self._get_single_commission_amount(com, subtotal, product, quantity))
        if 0.0 in res:
            res.remove(0.0)
        return min(res)
