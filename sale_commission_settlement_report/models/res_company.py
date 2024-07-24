from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    show_partner_settlement_report = fields.Boolean(
        "Show partner details in settlements report",
        default=False,
    )
    settlement_skip_zero_amount_lines = fields.Boolean(
        "Skip lines in settlements with zero amount",
        default=False,
    )
