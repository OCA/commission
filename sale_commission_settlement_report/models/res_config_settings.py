from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_partner_settlement_report = fields.Boolean(
        related="company_id.show_partner_settlement_report",
        readonly=False,
    )
    settlement_skip_zero_amount_lines = fields.Boolean(
        related="company_id.settlement_skip_zero_amount_lines",
        readonly=False,
    )
