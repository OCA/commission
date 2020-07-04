# © 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# Copyright 2020 Andrea Cometa - Apulia Software s.r.l.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):

        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if (self.invoice_id.type in ('out_invoice', 'out_refund') and
                self.invoice_id.partner_id and self.product_id):
            agent_list = []
            partner = self.invoice_id.partner_id
            for agent in partner.agents:
                # default commission_id for agent
                commission_id = agent.commission.id
                commission_id_product = self.env["product.product.agent"]\
                    .get_commission_id_product(self.product_id.id, agent)
                if commission_id_product:
                    commission_id = commission_id_product
                if commission_id:
                    agent_list.append({'agent': agent.id,
                                       'commission': commission_id
                                       })
            if agent_list:
                self.agents = False
                self.agents = agent_list

        return res
