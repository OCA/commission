import odoo.tests.common as common
from odoo.exceptions import ValidationError


class TestsaleCommissionAgentRestrict(common.TransactionCase):
    def setUp(self):
        super(TestsaleCommissionAgentRestrict, self).setUp()
        self.users_model = self.env["res.users"]
        self.partner_model = self.env["res.partner"]
        self.commission_model = self.env["sale.commission"]

    def test_sale_commission_agent_restrict(self):
        group_ids = self.env.ref("base.group_system").ids
        user_agent = self.users_model.create(
            {"name": "John", "login": "test1", "groups_id": [(6, 0, group_ids)]}
        )
        user_agent.partner_id.agent = True
        self.assertTrue(
            user_agent.has_group(
                "sale_commission_agent_restrict.group_agent_own_customers"
            )
        )
        user_agent.partner_id.agent = False
        self.assertFalse(
            user_agent.has_group(
                "sale_commission_agent_restrict.group_agent_own_customers"
            )
        )

        partner_agent1 = self.partner_model.create(
            {"name": "Johns Customer", "email": "john_test"}
        )
        self.assertNotIn(self.env.user.partner_id.id, partner_agent1.agent_ids.ids)

        user_agent.partner_id.agent = True
        group_partner_manager = self.env.ref("base.group_partner_manager")
        group_partner_manager.users = [(4, user_agent.id)]
        partner_agent2 = self.partner_model.with_user(user_agent.id).create(
            {"name": "Johns Customer 2", "email": "john_test2"}
        )
        self.assertIn(user_agent.partner_id.id, partner_agent2.agent_ids.ids)
        user_agent.write({"name": "New Name"})
        user_agent.partner_id.agent = False
        group1_id = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_customers"
        ).id
        group1_name = "in_group_" + str(group1_id)
        with self.assertRaises(ValidationError):
            user_agent.write({group1_name: True})
