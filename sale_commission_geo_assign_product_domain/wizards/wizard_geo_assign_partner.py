# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class WizardGeoAssign(models.TransientModel):
    _inherit = "wizard.geo.assign.partner"

    @api.model
    def update_partner_data(self, partner, agent):
        if agent.commission_type == "product_restricted":
            for line in agent.commission_geo_group_ids:
                if line.is_assignable(partner):
                    partner.agent_ids = [(4, agent.id)]
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
        else:
            super().update_partner_data(partner, agent)
