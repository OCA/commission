# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Abstract (http://www.abstract.it)
#    @author Davide Corio <davide.corio@abstract.it>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api
from openerp.tools.safe_eval import safe_eval as eval


class AccountInvoiceLineAgent(models.Model):
    _inherit = 'account.invoice.line.agent'

    @api.one
    @api.depends('commission.commission_type', 'invoice_line.price_subtotal')
    def _get_amount(self):
        if (self.commission.commission_type == 'formula' and
            not self.invoice_line.product_id.commission_free and
                self.commission):
            self.amount = 0.0
            formula = self.commission.formula
            results = {'line': self.invoice_line}
            eval(formula, results, mode="exec", nocopy=True)
            self.amount += float(results['result'])
        else:
            return super(AccountInvoiceLineAgent, self)._get_amount()
