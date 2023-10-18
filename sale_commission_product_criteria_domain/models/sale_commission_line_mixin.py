# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _get_commission_items(self, commission, product):
        # Method replaced
        categ_ids = {}
        categ = product.categ_id
        while categ:
            categ_ids[categ.id] = True
            categ = categ.parent_id
        categ_ids = list(categ_ids)

        # Module specific mod:
        if self.object_id._name == "sale.order.line":
            partner = self.object_id.order_id.partner_id
        elif self.object_id._name == "account.move.line":
            partner = self.object_id.partner_id
        else:
            partner = False
        if partner:
            group_ids = (
                partner.commission_item_agent_ids.filtered(
                    lambda x: x.agent_id == self.agent_id
                )
                .mapped("group_ids")
                .ids
            )
        else:
            group_ids = []

        # Select all suitable items. Order by best match
        # (priority is: all/cat/subcat/product/variant).
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                commission_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            LEFT JOIN commission_item_agent AS cia ON item.group_id = cia.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.commission_id = %s)
                AND (item.active = TRUE)
                AND (cia.id IS NULL OR cia.id = any(%s))
            ORDER BY
                item.applied_on, item.based_on, categ.complete_name desc
            """,
            (
                product.product_tmpl_id.ids,
                product.ids,
                categ_ids,
                commission._origin.id,
                group_ids,
            ),
        )
        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return item_ids
