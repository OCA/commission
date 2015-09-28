# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#    Copyright (C) 2015 Avanzosc (<http://www.avanzosc.es>)
#    Copyright (C) 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
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
from openerp import models, fields, api

from . import sale_commission as sc


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agents = fields.Many2many(
        comodel_name="res.partner", relation="partner_agent_rel",
        column1="partner_id", column2="agent_id",
        domain="[('agent', '=', True)]")
    # Fields for the partner when it acts as an agent
    agent = fields.Boolean(
        string="Creditor/Agent",
        help="Check this field if the partner is a creditor or an agent.")
    agent_type = fields.Selection(
        selection=[("agent", "External agent")], string="Type", required=True,
        default="agent")
    commissions = fields.Many2many(
        string="Commission", comodel_name="sale.commission",
        relation="agent_commission_rel",
        column1="partner_id", column2="commission_id",
        help="This is the default commission used in the sales where this "
             "agent is assigned. It can be changed on each operation if "
             "needed.")
    settlement = fields.Selection(
        selection=[(sc.PERIOD_MONTH, "Monthly"),
                   (sc.PERIOD_QUARTER, "Quarterly"),
                   (sc.PERIOD_SEMI, "Semi-annual"),
                   (sc.PERIOD_YEAR, "Annual")],
        string="Settlement period", default="monthly", required=True)
    settlements = fields.One2many(
        comodel_name="sale.commission.settlement", inverse_name="agent",
        readonly=True)

    @api.onchange('agent_type')
    def onchange_agent_type(self):
        if self.agent_type == 'agent':
            self.supplier = True
