# Copyright 2021 KMEE - Luis Felipe Mileo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerAgentTeam(models.Model):

    _name = 'res.partner.agent.team'
    _inherit = 'sale.commission.team.mixin'
    _description = 'Partner Agent Team'

    _order = 'sequence, partner_id, id'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True,
    )
