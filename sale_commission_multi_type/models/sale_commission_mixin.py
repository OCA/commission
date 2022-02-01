from odoo import fields, models


class SaleCommission(models.AbstractModel):
    _inherit = "sale.commission"

    sequence = fields.Integer(
        "Sequence", default=1, help="The first in the sequence is the default one."
    )


class SaleCommissionMixin(models.AbstractModel):
    _inherit = "sale.commission.mixin"

    def _prepare_agent_vals(self, agent):
        return {
            "agent_id": agent.id,
            "commission_id": agent.commission_id.id,
            "commission_ids": agent.commission_ids.ids,
        }


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"

    commission_ids = fields.Many2many(
        "sale.commission", domain=[("commission_type", "=", "cat_prod_var")]
    )
    applied_commission_id = fields.Many2one("sale.commission", readonly=True)
    commission_id = fields.Many2one(
        comodel_name="sale.commission",
        ondelete="restrict",
        required=False,
        compute="_compute_commission_id",
        store=True,
        readonly=False,
        copy=True,
    )

    def _get_commission_amount(
        self, commission, commissions, subtotal, product, quantity
    ):
        # Method replaced
        if commissions:
            return self._get_multi_commission_amount(
                commissions, subtotal, product, quantity
            )
        elif commission:
            return self._get_single_commission_amount(
                commission, subtotal, product, quantity
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
            ORDER BY
                item.applied_on, categ.complete_name desc, item.id desc
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

    def _get_multi_commission_amount(self, commissions, subtotal, product, quantity):
        for com in commissions:
            amount = self._get_single_commission_amount(
                com, subtotal, product, quantity
            )
            if amount > 0:
                # self.commission_ids = [(5, 0, 0)]
                return amount
        return 0
