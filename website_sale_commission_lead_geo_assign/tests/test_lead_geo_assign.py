# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestLeadGeoAssign(TransactionCase):

    def setUp(self):
        super(TestLeadGeoAssign, self).setUp()
        self.lead_model = self.env['crm.lead']
        self.partner_model = self.env['res.partner']
        self.wizard_model = self.env['wizard.geo.assign.lead']
        self.genova = self.env.ref('base.state_it_ge')
        self.not_found_tag = self.ref(
            'website_sale_commission_lead_geo_assign.'
            'tag_portal_lead_agent_not_found')

    def test_geo_assign_lead(self):
        lead_16137 = self.lead_model.create({
            'name': 'lead_16137',
            'zip': '16137',
        })
        lead_genova = self.lead_model.create({
            'name': 'lead_genova',
            'state_id': self.genova.id,
        })
        cron_params = dict(leads=(lead_genova | lead_16137))

        # No agent found in the system
        self.partner_model.search([('agent', '=', True)]).unlink()
        with self.assertRaises(UserError):
            self.lead_model.geo_assign_agents(**cron_params)

        agent_genova = self.partner_model.create({
            'name': 'agent_genova',
            'agent': True,
            'agent_state_ids': [(4, self.genova.id)]
        })

        lead_genova2 = self.lead_model.create({
            'name': 'lead_genova',
            'state_id': self.genova.id,
        })
        # Successfully assign agent_genova to lead_genova2 upon creation
        self.assertEqual(agent_genova, lead_genova2.partner_assigned_id)
        self.assertNotIn(self.not_found_tag, lead_genova2.tag_ids.ids)

        self.lead_model.geo_assign_agents(**cron_params)

        # Successfully assign agent_genova to lead_genova
        self.assertEqual(agent_genova, lead_genova.partner_assigned_id)
        self.assertNotIn(self.not_found_tag, lead_genova.tag_ids.ids)

        self.assertFalse(lead_16137.partner_assigned_id)
        self.assertIn(self.not_found_tag, lead_16137.tag_ids.ids)

        # Executing again the same wizard raises UserError
        # because check_existing_agents is True by default
        with self.assertRaises(UserError):
            self.lead_model.geo_assign_agents(**cron_params)

        cron_params.update(check_existing_agents=False)
        self.lead_model.geo_assign_agents(**cron_params)

        # If check_existing_agents is False, successfully reassign the agent
        self.assertEqual(agent_genova, lead_genova.partner_assigned_id)
        self.assertNotIn(self.not_found_tag, lead_genova.tag_ids.ids)

        self.assertFalse(lead_16137.partner_assigned_id)
        self.assertIn(self.not_found_tag, lead_16137.tag_ids.ids)

        # Create an agent for lead_16137
        agent_16137 = self.partner_model.create({
            'name': 'agent_16137',
            'agent': True,
            'agent_zip_from': '16100',
            'agent_zip_to': '17100',
        })
        self.lead_model.geo_assign_agents(**cron_params)

        # Now all the leads get an agent
        self.assertEqual(agent_genova, lead_genova.partner_assigned_id)
        self.assertNotIn(self.not_found_tag, lead_genova.tag_ids.ids)

        self.assertEqual(lead_16137.partner_assigned_id, agent_16137)
        self.assertNotIn(self.not_found_tag, lead_16137.tag_ids.ids)

        # Finally, check that the CRON executed on all the leads
        # raises UserError, if check_existing_agents is True
        # because some (our) leads already have an agent
        with self.assertRaises(UserError):
            self.lead_model.geo_assign_agents()
