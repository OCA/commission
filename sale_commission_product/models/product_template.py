# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    agent_id = fields.Many2one(
        "res.partner", string="Agent", domain="[('agent', '=', True)]"
    )
