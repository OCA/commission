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
from openerp import models, fields, api, exceptions, _


PERIOD_MONTH = "monthly"
PERIOD_QUARTER = "quaterly"
PERIOD_SEMI = "semi"
PERIOD_YEAR = "annual"


class SaleCommission(models.Model):
    _name = "sale.commission"
    _description = "Commission in sales"

    name = fields.Char('Name', required=True)
    commission_type = fields.Selection(
        selection=[("fixed", "Fixed percentage"),
                   ("section", "By sections")],
        string="Type", required=True, default="fixed")
    fix_qty = fields.Float(string="Fixed percentage")
    sections = fields.One2many(
        comodel_name="sale.commission.section", inverse_name="commission")
    active = fields.Boolean(default=True)
    period = fields.Selection(
        selection=[(PERIOD_MONTH, "Monthly"),
                   (PERIOD_QUARTER, "Every quarter"),
                   (PERIOD_SEMI, "Every semester"),
                   (PERIOD_YEAR, "Every year")],
        required=True, default=PERIOD_MONTH,
    )
    scope = fields.Selection(
        selection=[("own_sales", "On his customer sales"),
                   ("company_sales", "On company sales"),
                   ("own_margin", "On his customers margin"),
                   ("company_margin", "On company margin")],
        required=True, default="own_sales",
    )

    has_company_scope = fields.Boolean(compute="_compute_scope")
    has_own_scope = fields.Boolean(compute="_compute_scope")

    agent_ids = fields.Many2many(
        string="Agents", comodel_name="res.partner",
        relation="agent_commission_rel",
        column2="partner_id", column1="commission_id",
    )

    @api.one
    def _compute_scope(self):
        self.has_company_scope = self.scope in ("company_sales",
                                                "company_margin")
        self.has_own_scope = self.scope in ("own_sales", "own_margin")

    @api.multi
    def compute_sale_commission(self, sale_line):
        """ Compute the commission on a sale order line """
        if self.scope in ("own_sales", "company_sales"):
            base = sale_line.price_subtotal
        elif self.scope in ("own_margin", "company_margin"):
            # Compute margin: subtotal - unit cost * qty
            base = sale_line.price_subtotal - (
                sale_line.product_id.standard_price * sale_line.quantity
            )
        return self.compute_commission(
            sale_line.product_id,
            sale_line.price_subtotal,
        )

    # Currently implementation is the same, use same function. Both provided
    # to avoid breakage if we need different fields in invoice and SO
    compute_invoice_commission = compute_sale_commission

    @api.multi
    def compute_commission(self, product_id, price_subtotal):
        self.ensure_one()
        if product_id.commission_free:
            return 0.0

        if self.commission_type == 'fixed':
            return price_subtotal * (self.fix_qty / 100.0)
        elif self.commission_type == 'section':
            return self.calculate_section(price_subtotal)

    @api.multi
    def calculate_section(self, base):
        self.ensure_one()
        for section in self.sections:
            if section.amount_from <= base <= section.amount_to:
                return base * section.percent / 100.0
        return 0.0

    def get_default_commissions(self):
        partner_obj = self.env['res.partner']
        res = []
        if self.env.context.get('partner_id'):
            partner = partner_obj.browse(
                self.env.context['partner_id'])
            for agent in partner.agents:
                res.extend(
                    {'agent': agent.id,
                     'commission': comm.id}
                    for comm in agent.commissions
                    if comm.has_own_scope
                )
            for agent in partner_obj.search(
                    [('company_id', '=', partner.company_id.id),
                     ('agent', '=', True)]):
                res.extend(
                    {'agent': agent.id,
                     'commission': comm.id}
                    for comm in agent.commissions
                    if comm.has_company_scope
                )

        return res


class SaleCommissionSection(models.Model):
    _name = "sale.commission.section"
    _description = "Commission section"

    commission = fields.Many2one("sale.commission", string="Commission")
    amount_from = fields.Float(string="From")
    amount_to = fields.Float(string="To")
    percent = fields.Float(string="Percent", required=True)

    @api.one
    @api.constrains('amount_from', 'amount_to')
    def _check_amounts(self):
        if self.amount_to < self.amount_from:
            raise exceptions.ValidationError(
                _("The lower limit cannot be greater than upper one."))
