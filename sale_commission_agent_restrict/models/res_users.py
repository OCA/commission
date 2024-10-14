#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError

# -- List of predefined rules that must be managed
PREDEFINED_RULES = [
    "res.partner.rule.private.employee",
    "res.partner.rule.private.group",
]


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def tweak_access_rules(self):
        # Need to shut down non-updatable rules to ensure tweak is applied correctly
        rules = self.env["ir.rule"].sudo().search([("name", "in", PREDEFINED_RULES)])
        if rules:
            rules.sudo().write({"active": False})

    def write(self, values):
        # users partner must be an agent to have following groups
        group1_id = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_customers"
        ).id
        group2_id = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_commissions"
        ).id
        group1_name = "in_group_" + str(group1_id)
        group2_name = "in_group_" + str(group2_id)
        if group1_name in values or group2_name in values:
            for user in self:
                if not user.partner_id.agent:
                    raise ValidationError(
                        _(
                            "User {user} is not associated to any agent.\n"
                            "Please mark "
                            "partner corresponding to this user as agent "
                            "to be able to assign agent related group to him."
                        )
                        .format(
                            user=user.display_name,
                        )
                    )
        res = super(ResUsers, self).write(values)
        return res
