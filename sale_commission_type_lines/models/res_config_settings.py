# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_use_multi_type_commissions = fields.Boolean(
        "Use Multi Commission in Agent",
        config_parameter="sale_commission_type_lines.default_use_multi_type_commissions",
        default_model="res.partner",
        default=False,
    )

    default_based_on = fields.Selection(
        [("sol", "Any Sale Order Line"), ("discount", "Discount")],
        "Default Based On",
        config_parameter="sale_commission_type_lines.default_commission_based_on",
        default_model="commission.item",
        default="sol",
        required=True,
    )

    use_discount_in_ct_lines = fields.Boolean(
        "Use Discounts in Commission Lines",
        related="company_id.use_discount_in_ct_lines",
        readonly=False,
    )

    default_use_pricelist = fields.Boolean(
        "Pricelist in Commission Item",
        config_parameter="sale_commission_type_lines.default_use_commission_pricelist",
        default_model="commission.item",
        default=True,
    )

    display_invoiced_agent_icon = fields.Boolean(
        related="company_id.display_invoiced_agent_icon", readonly=False
    )
