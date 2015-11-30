# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class SaleCommissionMakeInvoice(models.TransientModel):
    _name = 'sale.commission.make.invoice'

    def _default_journal(self):
        return self.env['account.journal'].search(
            [('type', '=', 'purchase')])[0]

    def _default_settlements(self):
        return self.env.context.get('settlement_ids', [])

    def _default_from_settlement(self):
        return bool(self.env.context.get('settlement_ids'))

    journal = fields.Many2one(
        comodel_name='account.journal', required=True,
        domain="[('type', '=', 'purchase')]", default=_default_journal)
    product = fields.Many2one(
        comodel_name='product.product', string='Product for invoicing',
        required=True)
    settlements = fields.Many2many(
        comodel_name='sale.commission.settlement',
        relation="sale_commission_make_invoice_settlement_rel",
        column1='wizard_id', column2='settlement_id',
        domain="[('state', '=', 'settled')]", default=_default_settlements)
    from_settlement = fields.Boolean(default=_default_from_settlement)
    date = fields.Date()

    @api.multi
    def button_create(self):
        self.ensure_one()
        if not self.settlements:
            self.settlements = self.env['sale.commission.settlement'].search(
                [('state', '=', 'settled'), ('agent_type', '=', 'agent')])
        return self.settlements.make_invoices(
            self.journal, self.product, date=self.date)
