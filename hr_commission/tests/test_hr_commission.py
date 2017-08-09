# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from openerp.exceptions import ValidationError


class TestHrCommission(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrCommission, cls).setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'User example',
            'login': "user@example.com",
        })
        cls.partner = cls.user.partner_id
        cls.partner.supplier = True
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Employee example',
        })

    def test_hr_commission(self):
        # Check constrain without employee
        with self.assertRaises(ValidationError):
            self.partner.agent_type = 'salesman'
        self.assertEqual(self.partner.supplier, True)
        self.partner.agent_type = 'agent'
        # Ckeck onchange
        self.partner.agent_type = 'agent'
        self.employee.user_id = self.user.id
        self.partner.agent_type = 'salesman'
        self.partner.onchange_agent_type()
        self.assertEqual(self.partner.supplier, False)
        self.assertEqual(
            self.partner.employee_id,
            self.employee,
        )
