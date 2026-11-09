# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    commission_id = fields.Many2one(
        comodel_name="commission",
        ondelete="restrict",
        help="Default commission applied to lines sold under this pricelist "
        "when the matched pricelist rule has no commission of its own.",
    )


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    commission_id = fields.Many2one(comodel_name="commission", ondelete="restrict")
