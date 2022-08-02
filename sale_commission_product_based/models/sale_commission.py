#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleCommission (models.Model):
    _inherit = 'sale.commission'

    commission_type = fields.Selection(
        selection_add=[
            ("product_fallback", "Based on Product with Fallback Percentage"),
        ],
    )
    product_fallback_amount = fields.Float(
        string="Fallback Percentage for Product",
    )
    product_rule_ids = fields.One2many(
        comodel_name='sale.commission.product_rule',
        inverse_name='commission_id',
        string="Product rules",
    )

    def calculate_product_fallback(self, base, product):
        """
        Calculate amount for type 'Fixed and Based on Product Percentage'.
        """
        self.ensure_one()

        product_rules = self.product_rule_ids
        rule_match = product_rules.match_product(product)
        if rule_match:
            amount = rule_match.amount
        else:
            amount = self.product_fallback_amount

        return base * amount / 100.0
