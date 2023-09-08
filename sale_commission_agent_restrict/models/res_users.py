from odoo import _, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):
        # users partner must be an agent to have following groups
        group1_id = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_customers"
        ).id
        group2_id = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_commissions"
        ).id
        group1_name = "in_group_" + str(group1_id)
        group2_name = "in_group_" + str(group2_id)
        if group1_name in vals or group2_name in vals:
            if not self.partner_id.agent:
                raise ValidationError(
                    _(
                        "This user is not associated to any agent. "
                        "Please mark corresponding to this user partner as agent to be "
                        "able to assign agent related group to him."
                    )
                )
        return super().write(vals)
