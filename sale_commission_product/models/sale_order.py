# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id")
    def _compute_agent_ids(self):
        """
        Add agent if configured in product_template
        """
        super()._compute_agent_ids()
        for record in self.filtered(lambda x: x.product_id.product_tmpl_id.agent_id):
            partner = record.product_id.product_tmpl_id.agent_id
            if not record.agent_ids and partner.agent:
                record.agent_ids = [(0, 0, record._prepare_agent_vals(partner))]
