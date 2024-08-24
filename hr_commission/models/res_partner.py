# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, exceptions, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    agent_type = fields.Selection(
        selection_add=[("salesman", "Salesman (employee)")],
    )
    employee_id = fields.Many2one(
        string="Employee.",
        comodel_name="hr.employee",
        compute="_compute_employee_id",
        compute_sudo=True,
    )

    @api.depends('user_ids')
    def _compute_employee_id(self):
        for partner in self:
            if (len(partner.user_ids) == 1 and
                    len(partner.user_ids[0].employee_ids) == 1):
                partner.employee_id = partner.user_ids[0].employee_ids[0]

    @api.constrains('agent_type')
    def _check_employee(self):
        if self.agent_type == 'salesman' and not self.employee_id:
            raise exceptions.ValidationError(
                _("There must one (and only one) employee linked to this "
                  "partner. To do this, go to 'Human Resources' and check "
                  "'Employees'"))

    @api.onchange('agent_type')
    def onchange_agent_type_hr_commission(self):
        if self.agent_type == 'salesman':
            self.supplier = False
