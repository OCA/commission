# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
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
from openerp import models, fields


class commission(models.Model):
    """Object commission"""

    _name = "commission"
    _description = "Commission"

    name = fields.Char('Name', required=True)

    commission_type = fields.Selection(
        (("fixed", "Fix percentage"), ("section", "By sections")),
        string="Type",
        required=True,
        default="fixed"
    )

    fix_qty = fields.Float(string="Fix Percentage")

    sections = fields.One2many(
        "commission.section",
        "commission_id",
        string="Sections"
    )

    def calcula_tramos(self, cr, uid, ids, base, context=None):
        commission = self.browse(cr, uid, ids, context=context)[0]
        # Calculate sections
        for section in commission.sections:
            if base >= section.commission_from and (
                    base < section.commission_until or
                    section.commission_until == 0):
                res = base * section.percent / 100.0
                return res
        return 0.0


class commission_section(models.Model):
    """Commission section"""

    _name = "commission.section"
    _description = "Commission section"

    commission_from = fields.Float(string="From")

    commission_until = fields.Float(string="Until")

    percent = fields.Float(string="Percent")

    commission_id = fields.Many2one(
        "commission",
        string="Commission"
    )


class sale_agent(models.Model):
    """Sale agents"""

    _name = "sale.agent"
    _description = "Sale agent"

    name = fields.Char(
        string="Sale agent Name",
        required=True
    )

    agent_type = fields.Selection(
        (("adviser", "Adviser"), ("comercial", "Commercial")),
        string="Type",
        required=True,
        default="adviser"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        ondelete="cascade",
        help="Associated partner, is necessary for income invoices."
    )

    code = fields.Char(
        string="Code",
        related="partner_id.ref",
        readonly=True,
        help="Related company code"
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Associated Employee",
        help="Employee associated to agent, is necessary for set an employee "
             "to settle commissions in wage."
    )

    customer = fields.One2many(
        "res.partner.agent",
        "agent_id",
        string="Customer",
        readonly=True
    )

    commission = fields.Many2one(
        "commission",
        string="Commission by default",
        required=True
    )

    settlement = fields.Selection(
        (
            ("m", "Monthly"), ("t", "Quarterly"),
            ("s", "Semi-annual"), ("a", "Annual")
        ),
        string="Settlement period",
        default="m",
        required=True
    )

    active = fields.Boolean(string="Active", default=True)

    retention_id = fields.Many2one(
        "account.tax",
        string="Applied retention"
    )

    settlement_ids = fields.One2many(
        "settlement.agent",
        "agent_id",
        string="Settlements executed",
        readonly=True
    )

    def calcula_tramos(self, cr, uid, ids, base, context=None):
        """Calculate the sections by invoice"""
        agente = self.browse(cr, uid, ids, context=context)[0]
        return agente.commission.calcula_tramos(base)
