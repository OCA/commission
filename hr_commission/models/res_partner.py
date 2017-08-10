# -*- coding: utf-8 -*-
# Copyright 2015 Avanzosc (<http://www.avanzosc.es>)
# Copyright 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, exceptions, fields, models


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agent_type = fields.Selection(
        selection_add=[("salesman", "Salesman (employee)")],
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        compute="_compute_employee",
    )

    @api.depends('user_ids')
    def _compute_employee(self):
        for partner in self:
            partner.employee = False
            if len(partner.user_ids) != 1:
                continue
            if len(partner.user_ids[0].employee_ids) == 1:
                partner.employee_id = partner.user_ids[0].employee_ids[0]

    @api.constrains('agent_type', 'employee_id')
    def _check_employee(self):
        if self.agent_type == 'salesman' and not self.employee_id:
            raise exceptions.ValidationError(
                _("There must one (and only one) employee linked to this "
                  "partner. To do this, go to 'Human Resources' and check "
                  "'Employees'"))

    @api.multi
    @api.onchange('agent_type')
    def onchange_agent_type(self):
        if self.agent_type == 'salesman':
            self.supplier = False
        return super(ResPartner, self).onchange_agent_type()
