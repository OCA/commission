# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Avanzosc (<http://www.avanzosc.es>)
#    Copyright (C) 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agent_type = fields.Selection(
        selection_add=[("salesman", "Salesman (employee)")])
    employee = fields.Many2one(
        comodel_name="hr.employee", compute="_get_employee")
    users = fields.One2many(comodel_name="res.users",
                            inverse_name="partner_id")

    @api.one
    @api.depends('users')
    def _get_employee(self):
        self.employee = False
        if len(self.users) == 1 and len(self.users[0].employee_ids) == 1:
            self.employee = self.users[0].employee_ids[0]

    @api.constrains('agent_type', 'employee')
    def _check_employee(self):
        if self.agent_type == 'salesman' and not self.employee:
            raise exceptions.ValidationError(
                _("There must one (and only one) employee linked to this "
                  "partner. To do this, go to 'Human Resources' and check "
                  "'Employees'"))

    @api.onchange('agent_type')
    def onchange_agent_type(self):
        if self.agent_type == 'salesman':
            self.supplier = False
        return super(ResPartner, self).onchange_agent_type()
