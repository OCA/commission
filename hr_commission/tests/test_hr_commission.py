# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import exceptions
from odoo.tests import common


class TestHrCommission(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee = self.env['hr.employee'].create({
            'name': 'Test employee',
        })
        self.user = self.env['res.users'].create({
            'name': 'Test user',
            'login': 'test_hr_commission@example.org',
        })
        self.partner = self.user.partner_id

    def test_hr_commission(self):
        self.assertFalse(self.partner.employee_id)
        with self.assertRaises(exceptions.ValidationError):
            self.partner.agent_type = 'salesman'
        self.employee.user_id = self.user.id
        self.assertEqual(self.partner.employee_id, self.employee)
        # This shouldn't trigger exception now
        self.partner.agent_type = 'salesman'
        self.partner.supplier = True
        self.partner.onchange_agent_type_hr_commission()
        self.assertFalse(self.partner.supplier)
        # Check that un-assigning user in employee, it raises the constraint
        with self.assertRaises(exceptions.ValidationError):
            self.employee.user_id = False
