# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class WizardGeoAssign(models.TransientModel):
    _inherit = "wizard.geo.assign.partner"

    @api.model
    def update_partner_data(self, partner, agents):
        product_restricted_agents = agents.filtered(
            lambda a: a.commission_type == "product_restricted"
        )
        partner_agent_ids = self.env["res.partner"]
        for agent in product_restricted_agents:
            for line in agent.commission_geo_group_ids:
                if not line.is_assignable(partner):
                    continue
                partner_agent_ids += agent
                commission_item = partner.commission_item_agent_ids.filtered(
                    lambda x: x.agent_id == agent
                )
                if commission_item:
                    commission_item.group_ids = [
                        (4, x) for x in line.mapped("commission_group_ids.id")
                    ]
                else:
                    partner.commission_item_agent_ids = [
                        (
                            0,
                            0,
                            {
                                "agent_id": agent.id,
                                "group_ids": [
                                    (
                                        6,
                                        0,
                                        line.mapped("commission_group_ids.id"),
                                    )
                                ],
                            },
                        )
                    ]
        partner.agent_ids += partner_agent_ids
        super().update_partner_data(partner, agents - product_restricted_agents)
