# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def action_ship_create(self):
        """extend this method to add agent_id to picking"""
        res = super(SaleOrder, self).action_ship_create()
        for order in self:
            agents = [x.agent_id.id for x in order.sale_agent_ids]
            if agents:
                vals = {'agent_ids': [[6, 0, agents]], }
                for picking in order.picking_ids:
                    picking.write(vals)
        return res
