# Copyright 2018-2022 Tecnativa - Pedro M. Baeza
# Copyright 2024 Nextev Srl <odoo@nextev.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class CommissionMixin(models.AbstractModel):
    _inherit = "commission.mixin"

    def _prepare_agents_vals_partner(self, partner, settlement_type=None):
        """
        Utility method for adding agents set in product on agents dictionary creation
        """
        res = super()._prepare_agents_vals_partner(partner, settlement_type)
        agents = self.product_id.agent_ids
        if settlement_type:
            agents = agents.filtered(
                lambda x: not x.commission_id.settlement_type
                or x.commission_id.settlement_type == settlement_type
            )
        res += [(0, 0, self._prepare_agent_vals(agent)) for agent in agents]
        return res
