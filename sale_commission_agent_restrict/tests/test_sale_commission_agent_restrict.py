#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import Form, TransactionCase
from odoo.tools import mute_logger


class TestsaleCommissionAgentRestrict(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users_model = cls.env["res.users"]
        cls.partner_model = cls.env["res.partner"]
        cls.commission_model = cls.env["commission"]
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_partner_manager = cls.env.ref("base.group_partner_manager")
        cls.group_system = cls.env.ref("base.group_system")
        cls.group_own_customer = cls.env.ref(
            "sale_commission_agent_restrict.group_agent_own_customers"
        )
        cls.group_own_commissions = cls.env.ref(
            "sale_commission_agent_restrict.group_agent_own_commissions"
        )
        cls.payment_term_immediate = cls.env.ref(
            "account.account_payment_term_immediate"
        )
        cls.user_agent = cls.users_model.create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [
                    Command.set((cls.group_user + cls.group_partner_manager).ids)
                ],
            }
        )
        cls.user_agent.partner_id.agent = True
        cls.partner_agent = cls.env.ref("commission.res_partner_pritesh_sale_agent")

    def test_assign_group_to_agent(self):
        self.assertIn(self.group_own_customer, self.user_agent.groups_id)
        self.assertIn(self.group_own_commissions, self.user_agent.groups_id)

        self.user_agent.partner_id.agent = False
        self.assertNotIn(self.group_own_customer, self.user_agent.groups_id)
        self.assertNotIn(self.group_own_commissions, self.user_agent.groups_id)

        self.user_agent.partner_id.agent = True
        self.assertIn(self.group_own_customer, self.user_agent.groups_id)
        self.assertIn(self.group_own_commissions, self.user_agent.groups_id)

    def test_assign_agent_to_partner_created_by_agent(self):
        new_partner = self.partner_model.with_user(self.user_agent).create(
            {"name": "Test Partner 1"}
        )

        self.assertIn(self.user_agent.partner_id, new_partner.agent_ids)

        # Add to partner's agent but also preserve existing agents

        # `user_agent` is not able to access `partner_agent`.
        with self.assertRaises(AccessError) as ae:
            self.partner_model.with_user(self.user_agent).create(
                {
                    "name": "Test Partner 1",
                    "agent_ids": [Command.set(self.partner_agent.ids)],
                }
            )
        exc_message = ae.exception.args[0]
        self.assertIn("not allowed to access", exc_message)
        self.assertIn(self.partner_model._name, exc_message)

        # When `partner_agent` is fetched with sudo, it works as expected.
        self.partner_agent._fetch_field(self.partner_agent._fields["user_id"])
        new_partner = self.partner_model.with_user(self.user_agent).create(
            {
                "name": "Test Partner 1",
                "agent_ids": [Command.set(self.partner_agent.ids)],
            }
        )

        self.assertEqual(
            self.user_agent.partner_id + self.partner_agent,
            new_partner.sudo().agent_ids,
        )

    def test_sync_agents_to_children(self):
        """
        Field agent_ids on partner should sync to children contacts
        unless the agent is restricted to their own customers.
        In that case, the field should not be synced.
        """
        # agent_ids should sync normally
        parent = self.partner_model.create(
            {
                "name": "Test Partner 1",
                "street": "street",
                "agent_ids": [Command.set(self.partner_agent.ids)],
            }
        )
        child = self.partner_model.create(
            {"name": "Test Child 1", "parent_id": parent.id}
        )
        self.assertEqual(parent.street, child.street)
        self.assertEqual(parent.agent_ids, child.agent_ids)

        # agent_ids should not sync
        parent = self.partner_model.create(
            {
                "name": "Test Partner 2",
                "street": "street",
                "agent_ids": [Command.set(self.user_agent.partner_id.ids)],
            }
        )
        child = self.partner_model.create(
            {"name": "Test Child 2", "parent_id": parent.id}
        )
        self.assertEqual(parent.street, child.street)
        self.assertNotEqual(parent.agent_ids, child.agent_ids)
        self.assertFalse(child.agent_ids)

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_agent_own_customer(self):
        partner_no_agent = self.partner_model.create({"name": "Test Partner 1"})
        with self.assertRaises(AccessError):
            Form(partner_no_agent.with_user(self.user_agent))

        partner_with_agent = self.partner_model.create(
            {
                "name": "Test Partner 2",
                "agent_ids": [Command.set(self.user_agent.partner_id.ids)],
            }
        )
        Form(partner_with_agent.with_user(self.user_agent))

        # Can also read own partner
        Form(self.user_agent.partner_id.with_user(self.user_agent))

    def test_agent_cannot_change_payment_terms(self):
        partner_with_agent = self.partner_model.create(
            {
                "name": "Test Partner 1",
                "agent_ids": [Command.set(self.user_agent.partner_id.ids)],
            }
        )
        partner_with_agent.write({"property_payment_term_id": False})
        with self.assertRaises(UserError):
            partner_with_agent.with_user(self.user_agent).write(
                {"property_payment_term_id": False}
            )
        partner_with_agent.write({"property_supplier_payment_term_id": False})
        with self.assertRaises(UserError):
            partner_with_agent.with_user(self.user_agent).write(
                {"property_supplier_payment_term_id": False}
            )

        # Also cannot assign them on create
        with self.assertRaises(UserError):
            self.partner_model.with_user(self.user_agent).create(
                {
                    "name": "Test partner 2",
                    "property_payment_term_id": self.payment_term_immediate.id,
                }
            )
        with self.assertRaises(UserError):
            self.partner_model.with_user(self.user_agent).create(
                {
                    "name": "Test partner 3",
                    "property_supplier_payment_term_id": self.payment_term_immediate.id,
                }
            )
        # but can otherwise create a partner
        f = Form(self.partner_model)
        f.name = "Test partner 4"
        f.save()

    def test_agent_cannot_see_followers(self):
        self.partner_agent.message_subscribe(
            partner_ids=self.env.ref("base.partner_root").ids,
        )
        self.partner_agent.agent_ids = [Command.set(self.user_agent.partner_id.ids)]
        with Form(self.partner_agent) as f:
            self.assertTrue(f.message_follower_ids)

        with Form(self.partner_agent.with_user(self.user_agent)) as f:
            self.assertFalse(f.message_follower_ids)

    def test_cannot_assign_groups_to_not_agent(self):
        user = self.env.ref("base.user_admin")
        self.assertFalse(user.agent)
        group1_id = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_customers"
        ).id
        group1_name = "in_group_" + str(group1_id)
        with self.assertRaises(ValidationError):
            user.write({group1_name: True})
