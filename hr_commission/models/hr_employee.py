# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, exceptions, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def write(self, vals):
        """Check if there's an agent linked to that employee."""
        if "user_id" in vals and not vals["user_id"]:
            for emp in self:
                if emp.user_id.partner_id.agent_type == "salesman":
                    raise exceptions.ValidationError(
                        _(
                            "You can't remove the user, as it's linked to "
                            "a commission agent."
                        )
                    )
        return super().write(vals)
