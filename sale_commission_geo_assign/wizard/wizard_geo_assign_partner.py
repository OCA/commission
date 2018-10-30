# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class WizardGeoAssign(models.TransientModel):
    _name = 'wizard.geo.assign.partner'

    check_existing_agents = fields.Boolean(
        "Check existing agents",
        help="If checked, partners with already assigned agents will be "
             "blocked. Otherwise, found agents will be added",
        default=True
    )

    @api.multi
    def geo_assign_partner(self):
        self.ensure_one()
        partner_model = self.env['res.partner']
        agents = partner_model.search([('agent', '=', True)])
        if not agents:
            raise UserError(_("No agents found in the system"))
        partners = partner_model.browse(self.env.context.get('active_ids'))
        for partner in partners:
            if partner.agents and self.check_existing_agents:
                raise UserError(_(
                    "Partner %s already has agents. You should remove them"
                    " or deselect 'Check existing agents'"
                ) % partner.display_name)
            for agent in agents:
                if agent.is_assignable(partner):
                    partner.agents = [(4, agent.id)]
