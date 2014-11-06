# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#    All Rights Reserved
#    $Id$
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
from openerp import models, fields, _


class product_product(models.Model):

    _inherit = 'product.product'

    commission_exent = fields.Boolean(
        string="Commission exent",
        default=False
    )


class stock_picking(models.Model):

    _inherit = 'stock.picking'

    agent_ids = fields.Many2many(
        "sale.agent",
        string="Agentes"
    )

    # TODO: migrate this
    # def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id, context=None):
    #     '''Call after the creation of the invoice line'''
    #     if context is None:
    #         context = {}
    #     agent_pool = self.pool.get('invoice.line.agent')
    #     super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id, context=context)
    #     if move_line and move_line.sale_line_id and not move_line.sale_line_id.product_id.commission_exent:
    #         so_ref = move_line.sale_line_id.order_id
    #         for so_agent_id in so_ref.sale_agent_ids:
    #             vals = {
    #                 'invoice_line_id': invoice_line_id,
    #                 'agent_id': so_agent_id.agent_id.id,
    #                 'commission_id': so_agent_id.commission_id.id,
    #                 'settled': False
    #             }
    #             line_agent_id = agent_pool.create(cr, uid, vals, context=context)
    #             agent_pool.calculate_commission(cr, uid, [line_agent_id], context=context)
