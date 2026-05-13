#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

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

    def _get_partner_form_arch(self, user=None):
        partner = self.partner_model
        if user:
            partner = partner.with_user(user)
        view = self.env.ref("base.view_partner_form")
        result = partner.get_view(view_id=view.id, view_type="form")
        return etree.XML(result["arch"])

    def test_third_party_view_can_use_a_field_inside_the_page(self):
        """A field inside the page can be referenced by another view.

        A ``groups`` attribute on a node removes that node and every field it
        contains from the architecture, so a module that puts a field inside
        the page and references it outside the page is rejected while the view
        is validated. Removing the pages only when the view is served keeps the
        stored architecture free of restrictions and lets such a view exist.
        """
        field_name = "tz"
        arch = self._get_partner_form_arch()
        # The field must not be in the form yet: otherwise it would already be
        # available for every user and the test would prove nothing.
        self.assertFalse(arch.xpath("//field[@name='%s']" % field_name))

        view_arch = """
            <data>
                <xpath expr="//page[@name='sales_purchases']" position="inside">
                    <field name="%(field)s"/>
                </xpath>
                <xpath expr="//field[@name='category_id']" position="after">
                    <div attrs="{'invisible': [('%(field)s', '=', False)]}"/>
                </xpath>
            </data>
        """ % {
            "field": field_name
        }

        third_party_view = self.env["ir.ui.view"].create(
            {
                "name": "Third party view using a field inside the sales page",
                "model": "res.partner",
                "inherit_id": self.env.ref("base.view_partner_form").id,
                "arch": view_arch,
            }
        )
        self.assertTrue(third_party_view)

    def test_agent_does_not_get_the_pages(self):
        """The pages are removed for agents and kept for other users.

        The architecture is cached without the user in the cache key, so the
        pages have to be removed after the cache and only for the requesting
        user. Loading the form first as a non-agent exposes any mutation that
        leaks into the shared cache.
        """
        group = "sale_commission_agent_restrict.group_agent_own_commissions"
        # ``has_group`` is a plain SQL check: make sure the non-agent fixture
        # really is not an agent before using it as such.
        self.assertFalse(self.env.user.has_group(group))
        # Cold cache: the first caller really seeds it.
        self.env.registry.clear_caches()

        regular_arch = self._get_partner_form_arch()
        agent_arch = self._get_partner_form_arch(self.user_agent)

        self.assertTrue(regular_arch.xpath("//page[@name='sales_purchases']"))
        self.assertFalse(agent_arch.xpath("//page[@name='sales_purchases']"))
        self.assertFalse(agent_arch.xpath("//page[@name='internal_notes']"))
        # The hidden duplicates must stay available for the agent, other
        # modules use user_id and team_id in contexts and domains.
        self.assertTrue(agent_arch.xpath("//field[@name='user_id']"))
        self.assertTrue(agent_arch.xpath("//field[@name='team_id']"))

    def test_agent_view_without_pages_does_not_crash(self):
        """Agent forms that do not have those pages must still load."""
        # A cold cache makes sure the views are built while the agent asks for
        # them, which is when the pages are looked up.
        self.env.registry.clear_caches()

        partner = self.partner_model.with_user(self.user_agent)
        for view_ref in (
            "base.view_partner_simple_form",
            "base.view_partner_address_form",
            "base.res_partner_view_form_private",
        ):
            view = self.env.ref(view_ref)
            result = partner.get_view(view_id=view.id, view_type="form")
            self.assertIn("arch", result)

        # The address form built from the context has no such pages either.
        partner.with_context(force_email=True).get_view(view_type="form")
