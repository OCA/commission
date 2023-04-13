# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    display_invoiced_agent_icon = fields.Boolean(
        string="Display agent icon in SO after invoicing",
        default=True,
    )
    use_discount_in_ct_lines = fields.Boolean(
        "Use Discounts in Commission Lines",
        default=False,
    )
