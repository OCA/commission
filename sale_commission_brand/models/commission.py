# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleCommission(models.Model):
    _inherit = 'sale.commission'

    commission_type = fields.Selection(selection_add=[
        ('brand', 'Product Brand')])
    brand_lines = fields.One2many('sale.commission.brand', 'commission',
                                  string='Brand')


class SaleCommissionBrand(models.Model):
    _name = "sale.commission.brand"
    _description = "Commission Brand"

    commission = fields.Many2one("sale.commission", string="Commission",
                                 index=True)
    brand_id = fields.Many2one('product.brand', string='Brand', required=True)
    percent = fields.Float(string="Percent", required=True)
