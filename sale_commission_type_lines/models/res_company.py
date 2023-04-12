from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    display_invoiced_agent_icon = fields.Boolean(
        string="Display agent icon in SO after invoicing",
        default=True,
    )
