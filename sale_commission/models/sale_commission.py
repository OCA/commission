# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015-2016 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# © 2015-2016 Oihane Crucelaegui
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _


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

    @api.one
    @api.constrains('amount_from', 'amount_to')
    def _check_amounts(self):
        if self.amount_to < self.amount_from:
            raise exceptions.ValidationError(
                _("The lower limit cannot be greater than upper one."))
