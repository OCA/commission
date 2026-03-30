# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class CommissionLineMixin(models.AbstractModel):
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

    def _get_commission_items_domain(self, commission, product):
        # Method replaced
        categ_ids = {}
        categ = product.categ_id
        while categ:
            categ_ids[categ.id] = True
            categ = categ.parent_id
        categ_ids = list(categ_ids)
        return [
            ("commission_id", "=", commission.id),
            "|",
            ("product_tmpl_id", "=", False),
            ("product_tmpl_id", "=", product.product_tmpl_id.id),
            "|",
            ("product_id", "=", False),
            ("product_id", "=", product.id),
            "|",
            ("categ_id", "=", False),
            ("categ_id", "in", categ_ids),
        ]

    def _get_commission_item(self, commission, product):
        # Select all suitable items. Order by best match
        # (priority is: all/cat/subcat/product/variant).
        # In future versions use filtered_domain. Note: not used in this
        # version because exists a bug that is not returning the
        # correct result.
        return self.env["commission.item"].search(
            self._get_commission_items_domain(commission, product), limit=1
        )

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        self.ensure_one()
        commission_item = self._get_commission_item(commission, product)
        if not commission_item:
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

    def _get_discount_value(self, commission_item):
        # Will be overridden
        return self.object_id.discount
