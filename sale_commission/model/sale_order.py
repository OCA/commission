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
from openerp import models, fields, api, _


class sale_order_agent(models.Model):
    _name = "sale.order.agent"
    _rec_name = "agent_name"

    sale_id = fields.Many2one(
        "sale.order",
        string="Sale order",
        required=False,
        ondelete="cascade"
    )

    commission_id = fields.Many2one(
        "commission",
        string="Commission",
        required=False,
        ondelete="cascade"
    )

    agent_id = fields.Many2one(
        "sale.agent",
        string="Agent",
        required=True,
        ondelete="cascade"
    )

    agent_name = fields.Char(
        string="Agent name",
        related="agent_id.name"
    )

    @api.onchange("agent_id")
    def do_set_default_commission(self):
        """Set default commission when sale agent has changed"""
        self.commission_id = self.agent_id.commission

    @api.onchange("commission_id")
    def do_check_commission(self):
        """Check selected commission and raise a warning
        when selected commission is not the default provided for sale agent
        and default partner commission have sections
        """
        context = {}
        result = {}
        commission = self.commission_id
        if commission.id:
            agent_commission = self.agent_id.commission
            if self.agent_id and commission.sections:
                if commission.id != agent_commission.id:
                    return {
                        "warning": {
                            "title": _('Fee installments!'),
                            "message": _(
                                "Selected commission has been assigned "
                                "by sections and it does not match "
                                "the one defined to the selected agent."
                                "These sections shall apply only on this bill."
                            )
                        }
                    }


class sale_order(models.Model):
    """Include commission behavior in sale order model"""

    _inherit = "sale.order"

    sale_agent_ids = fields.One2many(
        "sale.order.agent",
        "sale_id",
        string="Agents",
        states={"draft": [("readonly", False)]}
    )

    # XXX: It doesn't work with Odoo v8.0 and I think it is not necessary
    # def create(self, cr, uid, values, context=None):
    #     """Add sale order reference on sale.order.agent
    #     """
    #     if context is None:
    #         context = {}
    #     agent_pool = self.pool.get('sale.order.agent')
    #     res = super(sale_order, self).create(cr, uid, values, context=context)
    #     if 'sale_agent_ids' in values:
    #         for sale_order_agent in values['sale_agent_ids']:
    #             agent_pool.write(cr, uid, sale_order_agent[1], {'sale_id': res})
    #     return res

    # XXX: It doesn't work with Odoo v8.0 and I think it is not necessary
    # def write(self, cr, uid, ids, values, context=None):
    #     """Rebuild sale.order reference on sale.order.agent
    #     """
    #     if context is None:
    #         context = {}
    #     agent_pool = self.pool.get('sale.order.agent')
    #     if 'sale_agent_ids' in values:
    #         for sale_order_agent in values['sale_agent_ids']:
    #             for id in ids:
    #                 if sale_order_agent[2]:
    #                     sale_order_agent[2]['sale_id'] = id
    #                 else:
    #                     agent_pool.unlink(cr, uid, sale_order_agent[1], context=context)
    #     return super(sale_order, self).write(cr, uid, ids, values, context=context)

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        """Agent id field will be changed according to new partner
        """
        if context is None:
            context = {}
        sale_agent_ids = []
        res = super(sale_order, self).onchange_partner_id(
            cr, uid, ids, part, context=context
        )
        if res.get('value', False) and part:
            sale_order_agent = self.pool.get('sale.order.agent')
            if ids:
                agent_id = sale_order_agent.search(
                    cr, uid,
                    [('sale_id', '=', ids)],
                    context=context
                )
                sale_order_agent.unlink(cr, uid, agent_id, context=context)
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.browse(cr, uid, part, context=context)
            for partner_agent in partner.commission_ids:
                vals = {
                    'agent_id': partner_agent.agent_id.id,
                    'commission_id': partner_agent.commission_id.id,
                    #'sale_id':ids
                }
                # FIXME: What is going on in this block?
                if ids:
                    for id in ids:
                        vals['sale_id'] = id
                sale_agent_id = sale_order_agent.create(
                    cr, uid, vals, context=context
                )
                sale_agent_ids.append(int(sale_agent_id))
            res['value']['sale_agent_ids'] = sale_agent_ids
        return res

    def action_ship_create(self, cr, uid, ids, context=None):
        """extend this method to add agent_id to picking"""
        if context is None:
            context = {}
        picking_pool = self.pool.get('stock.picking')
        res = super(sale_order, self).action_ship_create(
            cr, uid, ids, context=context
        )
        for order in self.browse(cr, uid, ids, context=context):
            pickings = [x.id for x in order.picking_ids]
            agents = [x.agent_id.id for x in order.sale_agent_ids]
            if pickings and agents:
                vals = {'agent_ids': [[6, 0, agents]], }
                picking_pool.write(cr, uid, pickings, vals, context=context)
        return res


class sale_order_line(models.Model):
    """It includes the commission in each invoice line
    when an invoice is created
    """

    _inherit = "sale.order.line"

    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_line_pool = self.pool.get('account.invoice.line')
        invoice_line_agent_pool = self.pool.get('invoice.line.agent')
        res = super(sale_order_line, self).invoice_line_create(
            cr, uid, ids, context
        )
        so_ref = self.browse(cr, uid, ids)[0].order_id
        for so_agent_id in so_ref.sale_agent_ids:
            inv_lines = invoice_line_pool.browse(cr, uid, res, context=context)
            for inv_line in inv_lines:
                exent = inv_line.product_id.commission_exent
                if inv_line.product_id and exent is not True:
                    vals = {
                        'invoice_line_id': inv_line.id,
                        'agent_id': so_agent_id.agent_id.id,
                        'commission_id': so_agent_id.commission_id.id,
                        'settled': False
                    }
                    line_agent_id = invoice_line_agent_pool.create(
                        cr, uid, vals, context=context
                    )
                    invoice_line_agent_pool.calculate_commission(
                        cr, uid, [line_agent_id], context=context
                    )
        return res
