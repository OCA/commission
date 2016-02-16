# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import exceptions
import openerp.tests.common as common


class TestHrCommission(common.TransactionCase):

    def setUp(self):
        super(TestHrCommission, self).setUp()
        self.user_model = self.env['res.users']
        self.partner_model = self.env['res.partner']
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
        })
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })
        self.eiffel_agent = self.browse_ref(
            'sale_commission.res_partner_eiffel_sale_agent')

    def test_compute_user(self):
        self.assertFalse(self.employee.user_id)
        self.assertFalse(self.user.partner_id.employee)
        self.employee.write({'user_id': self.user.id})
        self.assertNotEqual(len(self.employee.user_id.partner_id), 0)
        self.assertTrue(self.employee.user_id.partner_id.employee)

    def test_constraint(self):
        with self.assertRaises(exceptions.ValidationError):
            self.eiffel_agent.write({'agent_type': 'salesman'})

    def test_onchange(self):
        partner = self.partner_model.new({
            'name': 'Test Partner',
            'supplier': True,
            'agent_type': 'salesman',
        })
        self.assertTrue(partner.supplier)
        partner.onchange_agent_type()
        self.assertFalse(partner.supplier)
