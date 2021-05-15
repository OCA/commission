# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class ContractLine(models.Model):
    _inherit = 'contract.line'

    @api.model
    def _prepare_invoice_line(self, invoice_id=False, invoice_values=False):
        vals = super(ContractLine, self)._prepare_invoice_line(
            invoice_id=invoice_id, invoice_values=invoice_values)
        invoice_line_model = self.env['account.invoice.line'].with_context({
            'partner_id': self.contract_id.partner_id.id
        })
        vals = {} if vals is None else vals
        vals['agents'] = invoice_line_model._default_agents()
        return vals
