# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        for order in self:
            for line in order.order_line:
                for line_agent in line.agents:
                    if line_agent.agent.area_manager_id:
                        is_manager_already_there = False
                        for agent_line in line_agent.sale_line.agents:
                            if agent_line.agent == (
                                    line_agent.agent.area_manager_id):
                                is_manager_already_there = True
                        if not is_manager_already_there:
                            manager = line_agent.agent.area_manager_id
                            if line_agent.agent.commission_for_areamanager:
                                commission = (line_agent.
                                    agent.commission_for_areamanager.id)
                            else:
                                commission = manager.commission.id
                            line_agent.create({
                                'sale_line': line_agent.sale_line.id,
                                'agent': manager.id,
                                'commission': commission,
                                })
        return result
