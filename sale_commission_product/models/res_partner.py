# Copyright 2021 Andrea Cometa - Apulia Software s.r.l.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    product_agent_ids = fields.One2many(
        string="Product agent commissions",
        comodel_name='product.product.agent',
        inverse_name='agent_id')

    category_agent_ids = fields.One2many(
        string="Product agent commissions",
        comodel_name='product.category.agent',
        inverse_name='agent_id')
