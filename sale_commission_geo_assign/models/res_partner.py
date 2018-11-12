# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    agent_country_ids = fields.Many2many(
        'res.country', string='Countries',
        help='Countries where this agent operates'
    )
    agent_state_ids = fields.Many2many(
        'res.country.state', string='States',
        help='States where this agent operates'
    )
    agent_zip_from = fields.Char(
        'Zip From', help='ZIP range where this agent operates')
    agent_zip_to = fields.Char(
        'Zip To', help='ZIP range where this agent operates')

    @api.onchange('agent_country_ids')
    def onchange_countries(self):
        if self.agent_country_ids:
            domain = [('country_id', 'in', self.agent_country_ids.ids)]
        else:
            domain = []
        return {'domain': {
            'agent_state_ids': domain
        }}

    @api.multi
    def is_assignable(self, partner):
        # Check if agent (self) is assignable to 'partner'
        self.ensure_one()
        if (
            not self.agent_country_ids and not self.agent_state_ids and
            not self.agent_zip_from and not self.agent_zip_to
        ):
            # if no criteria set on agent, agent is excluded
            return False
        if (
            self.agent_country_ids and
            partner.country_id not in self.agent_country_ids
        ):
            return False
        if (
            self.agent_state_ids and
            partner.state_id not in self.agent_state_ids
        ):
            return False
        if (
            self.agent_zip_from and (partner.zip or '').upper() <
            self.agent_zip_from.upper()
        ):
            return False
        if (
            self.agent_zip_to and (partner.zip or '').upper() >
            self.agent_zip_to.upper()
        ):
            return False
        return True
