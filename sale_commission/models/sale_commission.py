# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


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
    invoice_state = fields.Selection(
        [('open', 'Invoice Based'),
         ('paid', 'Payment Based')], string='Invoice Status',
        required=True, default='open')
    amount_base_type = fields.Selection(
        selection=[('gross_amount', 'Gross Amount'),
                   ('net_amount', 'Net Amount')],
        string='Base', required=True, default='gross_amount')
    settlements = fields.Many2many(
        comodel_name='sale.commission.settlement')

    @api.multi
    def calculate_section(self, base):
        self.ensure_one()
        for section in self.sections:
            if section.amount_from <= base <= section.amount_to:
                return base * section.percent / 100.0
        return 0.0


class SaleCommissionSection(models.Model):
    _name = "sale.commission.section"
    _description = "Commission section"

    commission = fields.Many2one("sale.commission", string="Commission")
    amount_from = fields.Float(string="From")
    amount_to = fields.Float(string="To")
    percent = fields.Float(string="Percent", required=True)

    @api.multi
    @api.constrains('amount_from', 'amount_to')
    def _check_amounts(self):
        for section in self:
            if section.amount_to < section.amount_from:
                raise exceptions.ValidationError(
                    _("The lower limit cannot be greater than upper one."))
