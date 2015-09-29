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

from openerp import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):

        res = super(SaleOrderLine, self).product_id_change(cr, uid, ids,
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)

        product_obj = self.pool.get("product.product").browse(cr, uid, product)
        agent_list = []

        if partner_id:
            partner = self.pool.get("res.partner").browse(cr, uid, partner_id)
            for agent in partner.agents:
                commission_id = agent.commission.id
                if product_obj.commission:
                    commission_id = product_obj.commission
                agent_list.append({'agent': agent.id,
                                   'commission': commission_id
                                   })
            res['value']['agents'] = [(0, 0, x) for x in agent_list]

        return res
