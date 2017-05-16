# -*- coding: utf-8 -*-
# © 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='',
            type='out_invoice', partner_id=False, fposition_id=False,
            price_unit=False, currency_id=False, company_id=None):

        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty, name, type, partner_id,
            fposition_id, price_unit, currency_id, company_id)
        if type in ('out_invoice', 'out_refund') and partner_id and product:
            agent_list = []
            partner = self.env["res.partner"].browse(partner_id)
            for agent in partner.agents:
                # default commission_id for agent
                commission_id = agent.commission.id
                commission_id_product = self.env["product.product.agent"]\
                    .get_commission_id_product(product, agent)
                if commission_id_product:
                    commission_id = commission_id_product
                if commission_id:
                    agent_list.append({'agent': agent.id,
                                       'commission': commission_id
                                       })

                res['value']['agents'] = [(0, 0, x) for x in agent_list]

        return res
