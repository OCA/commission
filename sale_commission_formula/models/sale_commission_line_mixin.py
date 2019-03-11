#  -*- coding: utf-8 -*-
#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = 'sale.commission.line.mixin'

    @api.multi
    def _get_formula_input_dict(self):
        self.ensure_one()
        return {'line': self.object_id,
                'self': self}

    @api.multi
    def _get_commission_amount(
            self, commission, subtotal, commission_free, product, quantity):
        self.ensure_one()
        if commission.commission_type == 'formula' and \
                not commission_free and commission:
            formula = commission.formula
            results = self._get_formula_input_dict()
            safe_eval(formula, results, mode="exec", nocopy=True)
            return float(results['result'])
        return super(SaleCommissionLineMixin, self)._get_commission_amount(
            commission, subtotal, commission_free, product, quantity)
