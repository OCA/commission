# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrdeLine(models.Model):
    _inherit = "sale.order.line"

    def _get_partner_for_commission(self):
        return self.order_id.user_id.partner_id

    def _compute_agent_ids(self):
        """Add salesman agent if configured so and no other commission
        already populated.
        """
        super()._compute_agent_ids()
        for record in self.filtered(lambda x: x.order_id.partner_id):
            partner = record._get_partner_for_commission()
            if not record.agent_ids and partner.agent and partner.salesman_as_agent:
                record.agent_ids = [(0, 0, record._prepare_agent_vals(partner))]
