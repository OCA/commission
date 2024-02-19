# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    applied_commission_id = fields.Many2one("commission", readonly=True)
    commission_id = fields.Many2one(
        comodel_name="commission",
        ondelete="restrict",
        required=False,
        compute="_compute_commission_id",
        store=True,
        readonly=False,
        copy=True,
    )

    def _get_commission_items(self, commission, product):
        # Method replaced
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
                AND (item.active = TRUE)
            ORDER BY
                item.applied_on, item.based_on, categ.complete_name desc
            """,
            (
                product.product_tmpl_id.ids,
                product.ids,
                categ_ids,
                commission._origin.id,  # Added this
            ),
        )
        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return item_ids

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        self.ensure_one()
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return 0.0
        commission_item = self.env["commission.item"].browse(item_ids[0])
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

    def _get_discount_value(self, commission_item):
        # Will be overridden
        return self.object_id.discount
