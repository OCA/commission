# Copyright 2021 KMEE - Luis Felipe Mileo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmTeam(models.Model):

    _inherit = 'crm.team'

    agent_ids = fields.One2many(
        comodel_name='crm.team.agent',
        inverse_name='team_id',
    )
