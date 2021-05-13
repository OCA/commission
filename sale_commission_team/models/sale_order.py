# Copyright 2021 KMEE - Luis Felipe Mileo
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
            if not self and vals.get("order_id"):
                order = self.env["sale.order"].browse(vals["order_id"])

            if order.partner_id and order.team_id:
                return self._prepare_agents_team_vals_partner(
                    order.partner_id, order.team_id
                )
        return res
