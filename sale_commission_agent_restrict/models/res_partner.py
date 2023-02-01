from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, values):
        res = super(ResPartner, self).write(values)
        if len(self.user_ids) > 0 and "agent" in values:
            group_agent_own_customers = self.env.ref(
                "sale_commission_agent_restrict.group_agent_own_customers"
            )
            group_agent_own_commissions = self.env.ref(
                "sale_commission_agent_restrict.group_agent_own_commissions"
            )
            if values["agent"]:
                group_agent_own_customers.users = [
                    (4, user.id) for user in self._origin.user_ids
                ]
                group_agent_own_commissions.users = [
                    (4, user.id) for user in self._origin.user_ids
                ]
            else:
                group_agent_own_customers.users = [
                    (3, user.id) for user in self._origin.user_ids
                ]
                group_agent_own_commissions.users = [
                    (3, user.id) for user in self._origin.user_ids
                ]
        return res

    @api.model
    def create(self, vals):
        if self.env.user.partner_id.agent:
            vals["agent_ids"] = [(4, self.env.user.partner_id.id, 0)]
        res = super(ResPartner, self).create(vals)
        return res

    def _update_fields_values(self, fields):
        res = super(ResPartner, self)._update_fields_values(fields)
        if "agent_ids" in res.keys():
            for agent in self.agent_ids:
                for user_id in agent.user_ids:
                    if user_id and user_id.has_group(
                        "sale_commission_agent_restrict.group_agent_own_customers"
                    ):
                        # do not populate parents agent_ids to child partners
                        res.pop("agent_ids")
                        return res
        return res
