import odoo.tests.common as common
from odoo.exceptions import UserError


class TestSaleCommissionGeoAssign(common.TransactionCase):
    def setUp(self):
        super(TestSaleCommissionGeoAssign, self).setUp()
        self.partner_model = self.env["res.partner"]
        self.wizard_model = self.env["wizard.geo.assign.partner"]
        self.genova = self.env.ref("base.state_it_ge")

    def test_geo_assign(self):
        agents = self.partner_model.search([("agent", "=", True)])
        agents.write({'agent': False})
        wizard = self.wizard_model.create({})
        with self.assertRaises(UserError):
            wizard.geo_assign_partner()
        agents.write({'agent': True})
        c1 = self.partner_model.create(
            {
                "name": "c1",
                "zip": "16137",
            }
        )
        c2 = self.partner_model.create(
            {
                "name": "c2",
                "state_id": self.genova.id,
            }
        )
        agent1 = self.partner_model.create(
            {"name": "agent1", "agent": True, "agent_state_ids": [(4, self.genova.id)]}
        )
        wizard = self.wizard_model.with_context(active_ids=[c1.id, c2.id]).create({})
        wizard.geo_assign_partner()
        self.assertTrue(len(c2.agent_ids) == 1)
        self.assertTrue(agent1.id == c2.agent_ids[0].id)
        self.assertFalse(c1.agent)

        wizard = self.wizard_model.with_context(active_ids=[c1.id, c2.id]).create({})
        wizard.check_existing_agents = False
        wizard.geo_assign_partner()
        self.assertTrue(len(c2.agent_ids) == 1)
        self.assertTrue(agent1.id == c2.agent_ids[0].id)
        self.assertFalse(c1.agent)

        agent2 = self.partner_model.create(
            {
                "name": "agent2",
                "agent": True,
                "agent_zip_from": "16100",
                "agent_zip_to": "17100",
            }
        )
        wizard.geo_assign_partner()
        self.assertTrue(len(c2.agent_ids) == 1)
        self.assertTrue(len(c1.agent_ids) == 1)
        self.assertTrue(agent2.id == c1.agent_ids[0].id)

        wizard = self.wizard_model.with_context(active_ids=[c1.id, c2.id]).create({})
        wizard.check_existing_agents = True
        c1.agent_ids = [(6, 0, agent1.ids)]
        with self.assertRaises(UserError):
            wizard.geo_assign_partner()

        country_ids = self.env['res.country'].search([], limit=1)
        agent1.agent_country_ids = [(5, 0, 0)]
        agent1.is_assignable(c1)
        agent1.onchange_countries()
        agent1.agent_country_ids = [(6, 0, country_ids.ids)]
        agent1.is_assignable(c1)
        agent1.onchange_countries()
        c1.country_id = country_ids.id
        c1.state_id = agent1.agent_state_ids[0].id
        agent1.agent_zip_to = '111111'
        agent1.is_assignable(c1)
