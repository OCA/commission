from odoo.fields import Datetime
from odoo.tests import tagged, users

from odoo.addons.crm.tests.common import TestLeadConvertCommon


@tagged("crm_commission")
class TestCrmCommission(TestLeadConvertCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.agent = cls.env["res.partner"].create(
            {
                "name": "Agent Smith",
                "agent": True,
                "commission_id": cls.env["commission"]
                .create(
                    {
                        "name": "Test Commission 10%",
                        "fix_qty": 10.0,
                    }
                )
                .id,
            }
        )
        cls.agent_2 = cls.env["res.partner"].create(
            {
                "name": "Agent Jones",
                "agent": True,
                "commission_id": cls.env["commission"]
                .create(
                    {
                        "name": "Test Commission 5%",
                        "fix_qty": 5.0,
                    }
                )
                .id,
            }
        )
        date = Datetime.from_string("2020-01-20 16:00:00")
        cls.crm_lead_dt_mock.now.return_value = date

    def _convert_lead(self, lead, action="create", partner_id=False):
        """Helper to run the lead2opportunity wizard."""
        ctx = {
            "active_model": "crm.lead",
            "active_id": lead.id,
            "active_ids": lead.ids,
        }
        vals = {"action": action}
        if partner_id:
            vals["partner_id"] = partner_id
        convert = (
            self.env["crm.lead2opportunity.partner"].with_context(**ctx).create(vals)
        )
        convert.action_apply()
        return convert

    @users("user_sales_manager")
    def test_lead_agent_propagation_create(self):
        """Agent from lead is propagated to newly created partner."""
        lead = self.lead_1.with_user(self.env.user)
        lead.write({"lead_agent_ids": [(6, 0, self.agent.ids)]})

        self._convert_lead(lead, action="create")

        self.assertTrue(lead.partner_id, "Partner should have been created")
        self.assertIn(
            self.agent,
            lead.partner_id.agent_ids,
            "Agent should be propagated to the created partner",
        )

    @users("user_sales_manager")
    def test_lead_agent_propagation_exist(self):
        """Agent from lead is added to existing partner on conversion."""
        lead = self.lead_1.with_user(self.env.user)
        lead.write(
            {
                "lead_agent_ids": [(6, 0, self.agent.ids)],
                "partner_id": self.contact_1.id,
            }
        )

        self._convert_lead(lead, action="exist", partner_id=self.contact_1.id)

        self.assertEqual(lead.partner_id, self.contact_1)
        self.assertIn(
            self.agent,
            self.contact_1.agent_ids,
            "Agent should be added to the existing partner",
        )

    @users("user_sales_manager")
    def test_lead_agent_no_duplicate(self):
        """If partner already has the agent, it is not duplicated."""
        self.contact_1.write({"agent_ids": [(4, self.agent.id)]})
        lead = self.lead_1.with_user(self.env.user)
        lead.write(
            {
                "lead_agent_ids": [(6, 0, self.agent.ids)],
                "partner_id": self.contact_1.id,
            }
        )

        self._convert_lead(lead, action="exist", partner_id=self.contact_1.id)

        agent_count = len(self.contact_1.agent_ids.filtered(lambda a: a == self.agent))
        self.assertEqual(agent_count, 1, "Agent should not be duplicated")

    @users("user_sales_manager")
    def test_lead_no_agents(self):
        """Lead without agents does not alter partner agent_ids."""
        self.contact_1.write({"agent_ids": [(5, 0, 0)]})
        lead = self.lead_1.with_user(self.env.user)
        lead.write(
            {
                "lead_agent_ids": [(5, 0, 0)],
                "partner_id": self.contact_1.id,
            }
        )

        self._convert_lead(lead, action="exist", partner_id=self.contact_1.id)

        self.assertFalse(
            self.contact_1.agent_ids,
            "Partner should have no agents since lead had none",
        )

    @users("user_sales_manager")
    def test_lead_multiple_agents_create(self):
        """Multiple agents from lead are propagated to newly created partner."""
        lead = self.lead_1.with_user(self.env.user)
        lead.write(
            {
                "lead_agent_ids": [(6, 0, (self.agent | self.agent_2).ids)],
            }
        )

        self._convert_lead(lead, action="create")

        self.assertTrue(lead.partner_id)
        self.assertIn(self.agent, lead.partner_id.agent_ids)
        self.assertIn(self.agent_2, lead.partner_id.agent_ids)
