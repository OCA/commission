# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api
from openerp.tools.safe_eval import safe_eval


class SaleOrderLineAgent(models.Model):
    _inherit = 'sale.order.line.agent'

    @api.depends('commission.commission_type', 'sale_line.price_subtotal',
                 'commission.amount_base_type')
    def _compute_amount(self):
        for line_agent in self:
            if (line_agent.commission.commission_type == 'formula' and
                not line_agent.sale_line.product_id.commission_free and
                    line_agent.commission):
                line_agent.amount = 0.0
                formula = line_agent.commission.formula
                results = {'line': line_agent.sale_line}
                safe_eval(formula, results, mode="exec", nocopy=True)
                line_agent.amount += float(results['result'])
            else:
                return super(SaleOrderLineAgent, line_agent)._compute_amount()
