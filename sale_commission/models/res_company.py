from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    commission_show_settlement_dates = fields.Boolean(
        "Show invoice and payment dates in settlements",
    )
