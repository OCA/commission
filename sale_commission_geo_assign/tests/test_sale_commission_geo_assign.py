# -*- coding: utf-8 -*-

from odoo import exceptions
import odoo.tests.common as common


class TestSaleCommissionGeoAssign(common.TransactionCase):

    def setUp(self):
        super(TestSaleCommissionGeoAssign, self).setUp()
        self.partner_model = self.env['res.partner']
        self.wizard_model = self.env['wizard.geo.assign.partner']
        self.genova = self.env.ref('base.state_it_ge')

    def test_geo_assign(self):
        c1 = self.partner_model.create({
            'name': 'c1',
            'zip': '16137',
        })
        c2 = self.partner_model.create({
            'name': 'c2',
            'state_id': self.genova.id,
        })
        agent1 = self.partner_model.create({
            'name': 'agent1',
            'agent': True,
            'agent_state_ids': [(4, self.genova.id)]
        })
        wizard = self.wizard_model.with_context(
            active_ids=[c1.id, c2.id]).create({})
        wizard.geo_assign_partner()
        self.assertTrue(len(c2.agents) == 1)
        self.assertTrue(agent1.id == c2.agents.ids[0])
        self.assertFalse(c1.agents)

        wizard = self.wizard_model.with_context(
            active_ids=[c1.id, c2.id]).create({})
        with self.assertRaises(exceptions.UserError):
            wizard.geo_assign_partner()
        wizard.check_existing_agents = False
        wizard.geo_assign_partner()
        self.assertTrue(len(c2.agents) == 1)
        self.assertTrue(agent1.id == c2.agents.ids[0])
        self.assertFalse(c1.agents)

        agent2 = self.partner_model.create({
            'name': 'agent2',
            'agent': True,
            'agent_zip_from': '16100',
            'agent_zip_to': '17100',
        })
        wizard.geo_assign_partner()
        self.assertTrue(len(c2.agents) == 1)
        self.assertTrue(len(c1.agents) == 1)
        self.assertTrue(agent2.id == c1.agents.ids[0])
