# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class WizardGeoAssignLead(models.TransientModel):
    _name = 'wizard.geo.assign.lead'

    check_existing_agents = fields.Boolean(
        string="Check existing agents",
        help="If checked, leads with already assigned agents will be "
             "blocked. Otherwise, found agents will be added",
        default=True
    )

    @api.multi
    def _prepare_new_partner(self, lead):
        return {
            'street': lead.street,
            'street2': lead.street2,
            'zip': lead.zip,
            'city': lead.city,
            'country_id': lead.country_id.id,
            'state_id': lead.state_id.id
        }

    @api.multi
    def _new_partner(self, lead):
        return self.env['res.partner'].new(
            self._prepare_new_partner(lead))

    @api.multi
    def geo_assign_lead(self):
        """Assign an agent to the leads in active_ids"""
        self.ensure_one()
        partner_model = self.env['res.partner']
        all_agents = partner_model.search([('agent', '=', True)])
        if not all_agents:
            raise UserError(_("No agents found in the system"))
        lead_model = self.env['crm.lead']
        leads = lead_model.browse(self.env.context.get('active_ids'))
        not_found_tag = self.env.ref(
            'website_sale_commission_lead_geo_assign.'
            'tag_portal_lead_agent_not_found')
        for lead in leads:
            if lead.partner_assigned_id and self.check_existing_agents:
                raise UserError(_(
                    "Lead %s already has a partner assigned.\n"
                    "You should remove it or deselect 'Check existing agents'"
                ) % lead.display_name)

            # Remove the not_found_tag from the lead we are inspecting
            if not_found_tag in lead.tag_ids:
                lead.tag_ids = lead.tag_ids.filtered(
                    lambda t: t != not_found_tag)

            new_partner = self._new_partner(lead)
            for agent in all_agents:
                if agent.is_assignable(new_partner):
                    lead.partner_assigned_id = agent.id
                    break
            else:
                # If no agent is assignable, tag the lead
                lead.tag_ids |= not_found_tag
