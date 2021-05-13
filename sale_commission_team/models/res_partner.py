# Copyright 2021 KMEE - Luis Felipe Mileo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    agent_team_ids = fields.One2many(
        comodel_name='res.partner.agent.team',
        inverse_name='partner_id',
    )
