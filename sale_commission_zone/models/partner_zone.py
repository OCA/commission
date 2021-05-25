# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class PartnerZone(models.Model):

    _inherit = 'partner.zone'

    agent_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='agent_zone_rel',
        column1='zone_id',
        column2='agent_id',
        string='Agents',
    )
