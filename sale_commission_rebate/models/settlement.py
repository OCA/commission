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
