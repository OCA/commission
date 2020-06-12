# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrdeLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_agents_vals(self, vals=None):
        """Add salesman agent if configured so and no other commission
        already populated.
        """
        res = super()._prepare_agents_vals(vals=vals)
        if not res:
            partner = self.order_id.user_id.partner_id
            if not self and vals.get("order_id"):
                order = self.env["sale.order"].browse(vals["order_id"])
                partner = order.user_id.partner_id
            if partner.agent and partner.salesman_as_agent:
                res = [
                    (0, 0, {
                        'agent': partner.id,
                        'commission': partner.commission.id,
                    }),
                ]
        return res
