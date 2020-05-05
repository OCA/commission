# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleCommissionMakeInvoice(models.TransientModel):
    _inherit = 'sale.commission.make.invoice'

    journal = fields.Many2one(domain="")
