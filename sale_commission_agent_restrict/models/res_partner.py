#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, values):
        res = super().write(values)
        if 'agent' in values:
            linked_users = self.mapped('user_ids')
            if linked_users:
                group_agent_own_customers = self.env.ref(
                    "sale_commission_agent_restrict.group_agent_own_customers"
                )
                group_agent_own_commissions = self.env.ref(
                    "sale_commission_agent_restrict.group_agent_own_commissions"
                )
                if values["agent"]:
                    update_users = [
                        (4, user.id) for user in linked_users
                    ]
                else:
                    update_users = [
                        (3, user.id) for user in linked_users
                    ]
                group_agent_own_customers.users = update_users
                group_agent_own_commissions.users = update_users
        return res

    @api.model
    def create(self, vals):
        if self.env.user.partner_id.agent:
            vals["agents"] = [(4, self.env.user.partner_id.id, 0)]
        res = super(ResPartner, self).create(vals)
        return res
