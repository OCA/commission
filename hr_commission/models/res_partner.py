# -*- coding: utf-8 -*-
# © 2015 AvanzOSC
# © 2015-2016 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# © 2016 Oihane Crucelaegui
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agent_type = fields.Selection(
        selection_add=[("salesman", "Salesman (employee)")])
    employee = fields.Many2one(
        comodel_name="hr.employee", compute="_compute_employee")
    users = fields.One2many(comodel_name="res.users",
                            inverse_name="partner_id")

    @api.depends('users')
    def _compute_employee(self):
        for partner in self:
            partner.employee = False
            if len(partner.users) == 1 and\
                    len(partner.users[0].employee_ids) == 1:
                partner.employee = partner.users[0].employee_ids[0]

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
