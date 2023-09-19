import odoo.tests.common as common
from odoo.exceptions import UserError


class TestSaleCommissionGeoAssign(common.TransactionCase):
    def setUp(self):
        super(TestSaleCommissionGeoAssign, self).setUp()
        self.partner_model = self.env["res.partner"]
        self.wizard_model = self.env["wizard.geo.assign.partner"]
        self.country_genova = self.env.ref("base.state_it_ge")

        self.customer_1 = self.partner_model.create(
            {
                "name": "Customer 1",
                "zip": "16137",
            }
        )
        self.customer_2 = self.partner_model.create(
            {
                "name": "Customer 2",
                "state_id": self.country_genova.id,
            }
        )

        self.agent = self.partner_model.create(
            {
                "name": "Agent",
                "agent": True,
                "agent_state_ids": [(4, self.country_genova.id)],
            }
        )

    def test_geo_assign(self):
        wizard = self.wizard_model.with_context(
            active_ids=[self.customer_1.id, self.customer_2.id]
        ).create({})
        wizard.geo_assign_partner()
        self.assertTrue(len(self.customer_2.agent_ids) == 1)
        self.assertTrue(self.agent.id == self.customer_2.agent_ids[0].id)
        self.assertFalse(self.customer_1.agent)

        wizard = self.wizard_model.with_context(
            active_ids=[self.customer_1.id, self.customer_2.id]
        ).create({})
        wizard.check_existing_agents = False
        wizard.geo_assign_partner()
        self.assertTrue(len(self.customer_2.agent_ids) == 1)
        self.assertTrue(self.agent.id == self.customer_2.agent_ids[0].id)
        self.assertFalse(self.customer_1.agent)

        agent2 = self.partner_model.create(
            {
                "name": "agent2",
                "agent": True,
                "agent_zip_from": "16100",
                "agent_zip_to": "17100",
            }
        )
        wizard.geo_assign_partner()
        self.assertTrue(len(self.customer_2.agent_ids) == 1)
        self.assertTrue(len(self.customer_1.agent_ids) == 1)
        self.assertTrue(agent2.id == self.customer_1.agent_ids[0].id)

    def test_geo_assign_overwrite(self):
        new_agent = self.partner_model.create(
            {
                "name": "New Agent",
                "agent": True,
            }
        )

        self.customer_2.agent_ids = [(4, new_agent.id)]

        wizard = self.wizard_model.with_context(active_ids=[self.customer_2.id]).create(
            {}
        )
        wizard.replace_existing_agents = True
        wizard._onchange_replace_existing_agents()
        wizard.geo_assign_partner()
        self.assertEqual(self.customer_2.agent_ids, self.agent)

    def test_no_geo_assign_update(self):
        self.customer_1.no_geo_assign_update = True
        wizard = self.wizard_model.with_context(
            active_ids=[self.customer_1.id, self.customer_2.id]
        ).create({})
        with self.assertRaises(UserError):
            wizard.geo_assign_partner()

    def test_check_existing_agents(self):
        new_agent = self.partner_model.create(
            {
                "name": "New Agent",
                "agent": True,
            }
        )
        self.customer_2.agent_ids = [(4, new_agent.id)]

        wizard = self.wizard_model.with_context(
            active_ids=[self.customer_1.id, self.customer_2.id]
        ).create({})
        with self.assertRaises(UserError):
            wizard.geo_assign_partner()
        wizard.replace_existing_agents = True
        wizard._onchange_replace_existing_agents()
        wizard.geo_assign_partner()
        self.assertNotIn(new_agent, self.customer_2.agent_ids)
        self.assertEqual(self.customer_2.agent_ids, self.agent)
