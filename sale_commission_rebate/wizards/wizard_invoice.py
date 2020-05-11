# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class SaleCommissionMakeInvoice(models.TransientModel):
    _inherit = 'sale.commission.make.invoice'
    # Rebate invoices could choose a sales journal
    journal = fields.Many2one(domain="")
