# Copyright 2021 KMEE - Luis Felipe Mileo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CrmTeamAgent(models.Model):

    _name = 'crm.team.agent'
    _inherit = 'sale.commission.team.mixin'
    _description = 'Team Agent'
