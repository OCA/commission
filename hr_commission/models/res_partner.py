# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, exceptions, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    agent_type = fields.Selection(
        selection_add=[("salesman", "Salesman (employee)")],
    )
    employee_id = fields.Many2one(
        string="Related Employee",
        comodel_name="hr.employee",
        compute="_compute_employee_id",
        compute_sudo=True,
    )
    employee = fields.Boolean(compute="_compute_employee", store=True, readonly=False)

    @api.depends("user_ids")
    def _compute_employee_id(self):
        for partner in self:
            if len(partner.user_ids) == 1 and partner.user_ids[0].employee_ids:
                partner.employee_id = partner.user_ids[0].employee_ids[0]
            else:
                partner.employee_id = False

    @api.depends("agent_type", "employee_id")
    def _compute_employee(self):
        """Set the Boolean field according to the ResPartner-HrEmployee
        relation created here
        """
        if hasattr(super(), "_compute_employee"):
            super()._compute_employee()
        for record in self:
            if record.employee_id and record.agent_type == "salesman":
                record.employee = True
            else:
                record.employee = False

    @api.constrains("agent_type")
    def _check_employee(self):
        if self.agent_type == "salesman" and not self.employee_id:
            raise exceptions.ValidationError(
                _(
                    "There must one (and only one) employee linked to this "
                    "partner. To do this, go to 'Employees' and create an "
                    "Employee with a 'Related User' under 'HR Settings'."
                )
            )

    @api.onchange("agent_type")
    def onchange_agent_type_hr_commission(self):
        if self.agent_type == "salesman":
            self.supplier_rank = 0
