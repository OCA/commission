# Copyright (C) 2020, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_commission_automation_option = fields.\
        Selection([('partner', 'Partner'),
                   ('team', 'Sales Team'),
                   ('user', 'Salesperson')],
                  string='Automate Sale Order Agent Assignment By',
                  default='partner')
