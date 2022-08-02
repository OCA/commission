#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductRule (models.Model):
    _name = 'sale.commission.product_rule'
    _description = "Commission rule for product"
    _order = 'sequence'

    sequence = fields.Integer()
    product_category_id = fields.Many2one(
        comodel_name='product.category',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
    )
    commission_id = fields.Many2one(
        comodel_name='sale.commission',
        required=True,
        ondelete='cascade',
    )
    amount = fields.Float(
        string="Percentage",
    )

    _sql_constraints = [
        (
            'check_product_xor_category',
            """
            CHECK(
                (product_id IS NOT NULL AND product_category_id IS NULL)
                OR
                (product_id IS NULL AND product_category_id IS NOT NULL)
            )
            """,
            "Exactly one of 'Product' "
            "and 'Product Category' must have a value."),
    ]

    @api.multi
    def match_product(self, product):
        """
        Find which rule in self is a match for `product`.

        Rules are evaluated based on their `sequence`.
        A rule is a match for a product when the product is
        either the rule's product
        or has the rule's category.
        """
        for rule in self:
            if product == rule.product_id \
               or product.categ_id == rule.product_category_id:
                break
        else:
            rule = self.browse()
        return rule
