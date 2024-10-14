#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests.common as common

from odoo.exceptions import ValidationError
from odoo.addons.sale_commission.tests.test_common import TestCommon
from odoo.addons.sale_commission_agent_restrict.hooks import \
    restore_access_rules, \
    PREDEFINED_RULES


class TestSaleCommissionAgentRestrict (TestCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]

    def test_sale_commission_agent_restrict(self):
        user_agent = common.new_test_user(
            self.env,
            login='test1',
            groups='base.group_system',
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
        self.assertNotIn(self.env.user.partner_id.id, partner_agent1.agents.ids)

        user_agent.partner_id.agent = True
        group_partner_manager = self.env.ref("base.group_partner_manager")
        group_partner_manager.users = [(4, user_agent.id)]
        partner_agent2 = self.partner_model.sudo(user=user_agent.id).create(
            {"name": "Johns Customer 2", "email": "john_test2"}
        )
        self.assertIn(user_agent.partner_id.id, partner_agent2.agents.ids)
        user_agent.write({"name": "New Name"})
        user_agent.partner_id.agent = False
        group1_id = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_customers"
        ).id
        group1_name = "in_group_" + str(group1_id)
        with self.assertRaises(ValidationError):
            user_agent.write({group1_name: True})

    def test_current_agent_total(self):
        """
        'My Commission' field only shows current agent's commission.
        """
        # Arrange: Create a sale order having an agent
        agent = self.agent_quaterly
        sale_order = self._create_sale_order(
            agent,
            self.env.ref('sale_commission.demo_commission')
        )
        # pre-condition: 'My Commission' is zero if I am not the agent
        self.assertNotEqual(self.env.user.partner_id.agent, agent)
        self.assertEqual(sale_order.current_agent_total, 0)

        # Act: Create the agent's user
        user_agent_groups = [
            'base.group_system',
            'sale_commission_agent_restrict.group_agent_own_commissions',
            ]
        user_agent = common.new_test_user(
            self.env,
            login='user_agent_quarterly',
            groups=','.join(user_agent_groups),
            partner_id=agent.id,
        )

        # Assert: The agent's user
        # can read the order's commission in 'My Commission'
        agent_total = sale_order \
            .sudo(user=user_agent.id) \
            .current_agent_total
        self.assertEqual(
            agent_total,
            sale_order.commission_total
        )

    def test_restore_access_rules(self):
        """
        Some security rules are archived.
        The rules are activated on module uninstallation.
        """
        # pre-condition: The security rules are deactivated
        rules = self.env['ir.rule'] \
            .with_context(
                active_test=False,
            ) \
            .search(
            [
                ('name', 'in', PREDEFINED_RULES),
            ]
        )
        for rule in rules:
            self.assertFalse(
                rule.active,
                "Rule {rule} has not been archived".format(
                    rule=rule.display_name,
                )
            )

        # Act: call the uninstall hook
        restore_access_rules(self.env.cr, self.env.registry)

        # Assert: The security rules have been reactivated
        for rule in rules:
            self.assertTrue(
                rule.active,
                "Rule {rule} has not been activated".format(
                    rule=rule.display_name,
                )
            )
