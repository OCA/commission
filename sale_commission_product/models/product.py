# Copyright 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# Copyright 2024 Nextev Srl <odoo@nextev.it>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    agent_ids = fields.Many2many(
        string="Agents",
        comodel_name="res.partner",
        relation="product_agent_rel",
        column1="product_id",
        column2="agent_id",
        domain=[("agent", "=", True)],
        copy=True,
    )
