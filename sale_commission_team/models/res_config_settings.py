# Copyright (C) 2020, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_commission_automation_option = fields.\
        Selection([('partner', 'Partner'),
                   ('team', 'Sales Team'),
                   ('user', 'Salesperson')],
                  string='Sale Commission Automation',
                  related='company_id.sale_commission_automation_option',
                  default='partner',
                  readonly=False)
