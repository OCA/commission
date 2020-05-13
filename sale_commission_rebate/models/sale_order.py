# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def find_applicable_pricelist(agent):
        domain = [('name', '=', self.product_id.agent_id.id),
             ('product_id', '=', product.id),
             ('product_qty', '<=', quantity),
             ('date_start', '<=', self.product_id.agent_id.object_id.date),
             ('date_end', '>=', self.product_id.agent_id.date)]
        agent_info = self.env['product.supplierinfo'].search(domain)


    def _prepare_agents_vals(self):
        # agents taken from the products (rebates)
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_agents_vals()

        agent = self.product_id.agent_id
        if agent:
            agent_info = self.find_applicable_pricelist()
            if agent_info:
                res.append({
                    'agent': agent.id,
                    'commission': agent.commission.id,
                })
        return res
