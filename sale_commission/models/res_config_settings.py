from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    commission_show_settlement_dates = fields.Boolean(
        related="company_id.commission_show_settlement_dates",
        readonly=False,
    )
