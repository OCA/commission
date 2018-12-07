# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = 'sale.commission.line.mixin'

    @api.model
    def _get_formula_input_dict(self):
        return {
            'line': self.object_id,
            'self': self,
        }

    def _compute_amount(self):
        applicable_lines = self.filtered(lambda x: (
            not x.source_product_id.commission_free and x.commission
            and x.commission.commission_type == 'formula'
        ))
        for line in applicable_lines:
            formula = line.commission.formula
            results = line._get_formula_input_dict()
            safe_eval(formula, results, mode="exec", nocopy=True)
            line.amount = float(results['result'])
        rest = self - applicable_lines
        super(SaleCommissionLineMixin, rest)._compute_amount()
