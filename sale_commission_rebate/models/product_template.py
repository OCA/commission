# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # following similar approach as product_manufacturer
    agent_id = fields.Many2one('res.partner', 'Agent')
