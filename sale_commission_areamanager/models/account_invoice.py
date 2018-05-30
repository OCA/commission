# -*- coding: utf-8 -*-

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def compute_agents(self, line):
        for line_agent in line.agents:
            if line_agent.agent.area_manager_id:
                is_manager_already_there = False
                if line._table == 'account_invoice_line':
                    for agent_line in line_agent.invoice_line.agents:
                        if agent_line.agent == (
                                line_agent.agent.area_manager_id):
                            is_manager_already_there = True
                else:
                    for agent_line in line_agent.sale_line.agents:
                        if agent_line.agent == (
                                line_agent.agent.area_manager_id):
                            is_manager_already_there = True
                if not is_manager_already_there:
                    manager = line_agent.agent.area_manager_id
                    if line_agent.agent.commission_for_areamanager:
                        commission = (
                            line_agent.
                            agent.commission_for_areamanager.id)
                    else:
                        commission = manager.commission.id
                    if line._table == 'account_invoice_line':
                        line_agent.create({
                            'invoice_line': line.id,
                            'agent': manager.id,
                            'commission': commission,
                            })
                    else:
                        line_agent.create({
                            'sale_line': line.id,
                            'agent': manager.id,
                            'commission': commission,
                            })
        return True

    @api.multi
    def write(self, vals):
        result = super(AccountInvoice, self).write(vals)
        for invoice in self:
            for line in invoice.invoice_line_ids:
                invoice.compute_agents(line)
        return result
