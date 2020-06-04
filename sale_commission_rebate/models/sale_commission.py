# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class Commission(models.Model):
    _inherit = 'sale.commission'

    commission_type = fields.Selection(selection_add=[("rebate", "Rebate")])
