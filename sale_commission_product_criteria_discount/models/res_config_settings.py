# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_based_on = fields.Selection(
        [("sol", "Any Sale Order Line"), ("discount", "Discount")],
        config_parameter="sale_commission_product_criteria.default_commission_based_on",
        default_model="commission.item",
        default="sol",
        required=True,
    )
