# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api
from odoo.tools.safe_eval import safe_eval


class AccountInvoiceLineAgent(models.Model):
    _inherit = 'account.invoice.line.agent'

    @api.model
    def _get_formula_input_dict(self):
        return {'line': self.invoice_line,
                'self': self}

    @api.depends('commission.commission_type', 'invoice_line.price_subtotal',
                 'commission.amount_base_type')
    def _compute_amount(self):
        for line_obj in self:
            if (line_obj.commission.commission_type == 'formula' and
                not line_obj.invoice_line.product_id.commission_free and
                    line_obj.commission):
                line_obj.amount = 0.0
                formula = line_obj.commission.formula
                results = line_obj._get_formula_input_dict()
                safe_eval(formula, results, mode="exec", nocopy=True)
                line_obj.amount += float(results['result'])
                # Refunds commissions are negative
                if line_obj.invoice.type in ('out_refund', 'in_refund'):
                    line_obj.amount = -line_obj.amount
            else:
                return super(AccountInvoiceLineAgent, self)._compute_amount()
