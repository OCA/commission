# -*- coding: utf-8 -*-
# Copyright 2014-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_agents_vals(self):
        # agents taken from the products (rebates)
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_agents_vals()
        agent = self.product_id.agent_id
        res.append({
            'agent': agent.id,
            'commission': agent.commission.id,
        })
        return res
