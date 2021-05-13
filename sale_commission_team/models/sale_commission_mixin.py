# Copyright 2021 KMEE - Luis Felipe Mileo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleCommissionMixin(models.AbstractModel):
    _inherit = 'sale.commission.mixin'

    @api.model
    def _prepare_agents_team_vals_partner(self, partner_id, team_id):
        """Utility method for getting agents of a partner."""

        agent_team_ids = partner_id.agent_team_ids.filtered(
            lambda x: x.team_id == team_id
        )
        # TODO: Limit one partner/agent/team by configuration
        rec = []
        for agent_team_id in agent_team_ids:
            rec.append((0, 0, {
                'agent': agent_team_id.agent_id.id,
                'commission': agent_team_id.commission.id,
            }))
        return rec
