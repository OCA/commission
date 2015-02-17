# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Inform??ticos (<http://www.pexego.es>).
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


class SaleOrderAgent(models.Model):
    _name = "sale.order.agent"
    _rec_name = "agent_name"

    sale_id = fields.Many2one("sale.order", string="Sale order",
                              required=False, ondelete="cascade")
    commission_id = fields.Many2one("commission", string="Commission",
                                    required=False, ondelete="cascade")
    agent_id = fields.Many2one("sale.agent", string="Agent", required=True,
                               ondelete="cascade")
    agent_name = fields.Char(string="Agent name", related="agent_id.name")

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


class SaleOrder(models.Model):
    """Include commission behavior in sale order model"""
    _inherit = "sale.order"

    sale_agent_ids = fields.One2many("sale.order.agent", "sale_id",
                                     string="Agents", copy=True,
                                     states={"draft": [("readonly", False)]})

    @api.multi
    @api.onchange("partner_id")
    def onchange_partner_id(self, part):
        """Agent id field will be changed according to new partner"""
        sale_agent_ids = []
        partner_obj = self.env['res.partner']
        res = super(SaleOrder, self).onchange_partner_id(part)
        if res.get('value') and part:
            partner = partner_obj.browse(part)
            for partner_agent in partner.agent_ids:
                vals = {
                    'agent_id': partner_agent.agent_id.id,
                    'commission_id': partner_agent.commission_id.id,
                }
                for sale_id in self.ids:
                    vals['sale_id'] = sale_id
                sale_agent_ids.append(tuple([0, 0, vals]))
            res['value']['sale_agent_ids'] = sale_agent_ids
        return res


class SaleOrderLine(models.Model):
    """It includes the commission in each invoice line when an invoice is
    created"""
    _inherit = "sale.order.line"

    @api.multi
    def invoice_line_create(self):
        invoice_line_pool = self.env['account.invoice.line']
        invoice_line_agent_pool = self.env['invoice.line.agent']
        res = super(SaleOrderLine, self).invoice_line_create()
        data = self[0]
        for so_agent_id in data.order_id.sale_agent_ids:
            inv_lines = invoice_line_pool.browse(res)
            for inv_line in inv_lines:
                commission_free = inv_line.product_id.commission_free
                if inv_line.product_id and commission_free is not True:
                    vals = {
                        'invoice_line_id': inv_line.id,
                        'agent_id': so_agent_id.agent_id.id,
                        'commission_id': so_agent_id.commission_id.id,
                        'settled': False
                    }
                    line_agent = invoice_line_agent_pool.create(vals)
                    line_agent.calculate_commission()
        return res
