# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 Asr Oss (http://www.asr-oss.com)
#                       Alejandro Sanchez Ramirez <alejandro@asr-oss.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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

        if partner_id and product:
            agent_list = []
            partner = self.env["res.partner"].browse(partner_id)
            for agent in partner.agents:
                # default commission_id for agent
                commission_id = agent.commission.id
                commission_id_product = self.env["product.template.agent"]\
                    .get_commission_id_product(product, agent)
                if commission_id_product:
                    commission_id = commission_id_product
                agent_list.append({'agent': agent.id,
                                   'commission': commission_id
                                   })

                res['value']['agents'] = [(0, 0, x) for x in agent_list]

        return res
