# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"

    def _prepare_invoice_line(self, settlement, invoice, product):
        res = super(Settlement, self)._prepare_invoice_line(settlement, invoice, product)
        if res.get('price_unit', False) and settlement.agent_type == 'rebate':
            res['price_unit'] = settlement.total
        return res

def _prepare_invoice_header(self, settlement, journal, date=False):
    if settlement.agent_type == 'rebate':
        invoice = self.env['account.invoice'].new({
            'partner_id': settlement.agent.id,
            'type': 'in_refund',
            'date_invoice': date,
            'journal_id': journal.id,
            'company_id': settlement.company_id.id,
            'state': 'draft',
        })
        # Get other invoice values from onchanges
        invoice._onchange_partner_id()
        invoice._onchange_journal_id()
        return invoice._convert_to_write(invoice._cache)
    else:
        return super()._prepare_invoice_header(settlement, journal, date)
