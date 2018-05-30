# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        for order in self:
            for line in order.order_line:
                self.env['account.invoice'].compute_agents(line)
        return result
