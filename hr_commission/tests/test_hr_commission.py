# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import exceptions

from odoo.addons.commission.tests.test_commission import TestCommissionBase


class TestHrCommission(TestCommissionBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Test employee"})
        cls.user = cls.env["res.users"].create(
            {"name": "Test user", "login": "test_hr_commission@example.org"}
        )
        cls.partner = cls.user.partner_id

    def test_hr_commission(self):
        self.assertFalse(self.partner.employee_id)
        with self.assertRaises(exceptions.ValidationError):
            self.partner.agent_type = "salesman"
        self.employee.user_id = self.user.id
        self.assertEqual(self.partner.employee_id, self.employee)
        # This shouldn't trigger exception now
        self.partner.agent_type = "salesman"
        self.assertTrue(self.partner.employee)
        # Check that un-assigning user in employee, it raises the constraint
        with self.assertRaises(exceptions.ValidationError):
            self.employee.user_id = False

    def test_mark_to_invoice(self):
        settlements = self._create_settlement(
            self.partner,
            self.commission_section_paid,
        )
        self.assertEqual(settlements.state, "settled")
        settlements.mark_as_invoiced()
        self.assertEqual(settlements.state, "invoiced")
