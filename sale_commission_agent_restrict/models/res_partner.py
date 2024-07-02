#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def assign_remove_agent_groups(self, is_agent):
        group_agent_own_customers = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_customers"
        )
        group_agent_own_commissions = self.env.ref(
            "sale_commission_agent_restrict.group_agent_own_commissions"
        )
        if is_agent:
            self.user_ids.write(
                {
                    "groups_id": [
                        Command.link(group_agent_own_customers.id),
                        Command.link(group_agent_own_commissions.id),
                    ]
                }
            )
        else:
            self.user_ids.write(
                {
                    "groups_id": [
                        Command.unlink(group_agent_own_customers.id),
                        Command.unlink(group_agent_own_commissions.id),
                    ]
                }
            )

    @api.model
    def check_agent_changing_payment_terms(self, vals):
        if self.env.user.partner_id.agent:
            forbidden_fields = [
                "property_payment_term_id",
                "property_supplier_payment_term_id",
            ]
            # if self is an empty recordset, we're in a create
            is_create = not self
            for field in forbidden_fields:
                # allow empty value in a create
                # workaround for form filling this field automatically
                if is_create and not vals.get(field):
                    continue
                if field in vals:
                    raise UserError(
                        _("Agents are not allowed to change Contacts' payment terms")
                    )

    @api.model
    def check_agent_changing_agents(self, vals):
        if self.env.user.partner_id.agent:
            if "agent_ids" in vals:
                raise UserError(
                    _(
                        "Agents are not allowed to change the agents assigned to a Contact"
                    )
                )

    def write(self, vals):
        self.check_agent_changing_payment_terms(vals)
        self.check_agent_changing_agents(vals)
        res = super().write(vals)
        if "agent" in vals and self.user_ids:
            self.assign_remove_agent_groups(vals["agent"])
        return res

    @api.model_create_multi
    def create(self, vals_list):
        current_user_partner = self.env.user.partner_id
        for vals in vals_list:
            self.check_agent_changing_payment_terms(vals)
            if current_user_partner.agent:
                # extra safe, but the field should never be pre-populated because
                # agent cannot see the field agent_ids in the form view
                vals["agent_ids"] = vals.get("agent_ids", []) + [
                    Command.link(current_user_partner.id)
                ]
        return super().create(vals_list)

    def _update_fields_values(self, fields):
        res = super()._update_fields_values(fields)
        if "agent_ids" in res.keys():
            for agent in self.agent_ids:
                for user_id in agent.user_ids:
                    if user_id and user_id.has_group(
                        "sale_commission_agent_restrict.group_agent_own_commissions"
                    ):
                        # do not populate parents agent_ids to child partners
                        res.pop("agent_ids")
                        return res
        return res
