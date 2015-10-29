# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, fiscal_position):
        res = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, fiscal_position)
        invoice_line_model = self.env['account.invoice.line'].with_context(
            partner_id=line.analytic_account_id.partner_id.id)
        res = {} if res is None else res
        res['agents'] = invoice_line_model._default_agents()
        return res
