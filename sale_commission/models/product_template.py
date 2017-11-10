# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    commission_free = fields.Boolean(string="Free of commission",
                                     default=False)
