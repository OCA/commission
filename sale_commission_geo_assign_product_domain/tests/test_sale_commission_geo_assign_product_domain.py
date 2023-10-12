# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestSaleCommissionGeoAssignProductDomain(common.TransactionCase):
    def setUp(self):
        super(TestSaleCommissionGeoAssignProductDomain, self).setUp()
        self.partner_model = self.env["res.partner"]
        self.commission_group_model = self.env["res.partner.commission.group"]
        self.commission_item_group_model = self.env["commission.items.group"]
        self.wizard_model = self.env["wizard.geo.assign.partner"]

        self.country_italy = self.env.ref("base.it")
        self.country_spain = self.env.ref("base.es")
        self.state_genova = self.env.ref("base.state_it_ge")

        self.commission_rules = self.env.ref(
            "sale_commission_product_criteria.demo_commission_rules"
        )
        self.commission_rules_restrict = self.env.ref(
            "sale_commission_product_criteria_domain.demo_commission_rules_restrict"
        )

        self.cig_italy = self.env.ref(
            "sale_commission_product_criteria_domain.demo_cig_italy"
        )
        self.cig_spain = self.env.ref(
            "sale_commission_product_criteria_domain.demo_cig_spain"
        )
        self.cig_empty = self.commission_item_group_model.create(
            {
                "name": "Empty",
                "commission_ids": [(6, 0, [self.commission_rules_restrict.id])],
            }
        )

    def test_geo_assign(self):
        c_it = self.partner_model.create(
            {
                "name": "Customer Italy",
                "country_id": self.country_italy.id,
                "state_id": self.state_genova.id,
            }
        )
        c_es = self.partner_model.create(
            {
                "name": "Customer Spain",
                "country_id": self.country_spain.id,
            }
        )
        agent = self.partner_model.create(
            {
                "name": "Agent Spain and Italy",
                "agent": True,
                "commission_id": self.commission_rules_restrict.id,
                "allowed_commission_group_ids": [
                    (6, 0, [self.cig_italy.id, self.cig_spain.id])
                ],
            }
        )

        self.commission_group_model.create(
            [
                {
                    "partner_id": agent.id,
                    "country_ids": [(6, 0, [self.country_italy.id])],
                    "state_ids": [(6, 0, [self.state_genova.id])],
                    "commission_group_ids": [(6, 0, [self.cig_italy.id])],
                },
                {
                    "partner_id": agent.id,
                    "country_ids": [(6, 0, [self.country_spain.id])],
                    "commission_group_ids": [(6, 0, [self.cig_spain.id])],
                },
                {
                    "partner_id": agent.id,
                    "commission_group_ids": [(6, 0, [self.cig_empty.id])],
                },
            ]
        )

        wizard = self.wizard_model.with_context(active_ids=[c_it.id, c_es.id]).create(
            {}
        )
        wizard.geo_assign_partner()

        self.assertEqual(c_it.agent_ids, agent)
        self.assertEqual(c_it.commission_item_agent_ids.group_ids, self.cig_italy)

        self.assertEqual(c_es.agent_ids, agent)
        self.assertEqual(c_es.commission_item_agent_ids.group_ids, self.cig_spain)

    def test_geo_assign_twice(self):
        c_it = self.partner_model.create(
            {
                "name": "Customer Italy",
                "country_id": self.country_italy.id,
                "state_id": self.state_genova.id,
            }
        )

        agent = self.partner_model.create(
            {
                "name": "Agent Spain and Italy",
                "agent": True,
                "commission_id": self.commission_rules_restrict.id,
                "allowed_commission_group_ids": [
                    (6, 0, [self.cig_italy.id, self.cig_spain.id])
                ],
            }
        )

        self.commission_group_model.create(
            [
                {
                    "partner_id": agent.id,
                    "country_ids": [(6, 0, [self.country_italy.id])],
                    "commission_group_ids": [(6, 0, [self.cig_italy.id])],
                },
                {
                    "partner_id": agent.id,
                    "state_ids": [(6, 0, [self.state_genova.id])],
                    "commission_group_ids": [(6, 0, [self.cig_spain.id])],
                },
            ]
        )

        wizard = self.wizard_model.with_context(active_ids=c_it.ids).create({})

        # Should not raise an error
        wizard.geo_assign_partner()
        self.assertEqual(c_it.agent_ids, agent)
        self.assertIn(self.cig_italy.id, c_it.commission_item_agent_ids.group_ids.ids)
        self.assertIn(self.cig_spain.id, c_it.commission_item_agent_ids.group_ids.ids)

    def test_change_commission_type(self):
        agent = self.partner_model.create(
            {
                "name": "Agent Spain and Italy",
                "agent": True,
                "commission_id": self.commission_rules.id,
                "allowed_commission_group_ids": [
                    (6, 0, [self.cig_italy.id, self.cig_spain.id])
                ],
                "agent_country_ids": [(6, 0, [self.country_italy.id])],
                "agent_state_ids": [(6, 0, [self.state_genova.id])],
                "agent_zip_from": 31234,
                "agent_zip_to": 31333,
            }
        )
        self.assertNotEqual(agent.commission_type, "product_restricted")

        agent.write(
            {
                "commission_id": self.commission_rules_restrict.id,
            }
        )
        self.assertEqual(agent.commission_type, "product_restricted")
        agent._onchange_commission_type()
        self.assertFalse(agent.agent_country_ids)
        self.assertFalse(agent.agent_state_ids)
        self.assertFalse(agent.agent_zip_from)
        self.assertFalse(agent.agent_zip_to)
