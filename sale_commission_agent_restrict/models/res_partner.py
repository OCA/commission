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

    @api.model
    def _commercial_fields(self):
        res = super()._commercial_fields()
        for agent in self.agent_ids:
            user_id = self.env["res.users"].search([("partner_id", "=", agent.id)])
            if (
                "agent_ids" in res
                and user_id
                and user_id.has_group(
                    "sale_commission_agent_restrict.group_agent_own_customers"
                )
            ):
                res.remove("agent_ids")
        return res
