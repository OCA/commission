# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2020 ElvenStudio - Vincenzo Terzulli <v.terzulli@elvenstudio.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import api, models

import logging
_log = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def get_commission_from_pricelist(self):
        self.ensure_one()
        res = False
        if self.product_id and self.invoice_id.partner_id.property_product_pricelist:
            pricelist = self.invoice_id.partner_id.property_product_pricelist
            pr_dict = pricelist.price_rule_get_multi(
                products_by_qty_by_partner=[(self.product_id,
                                             self.quantity or 1.0,
                                             self.invoice_id.partner_id)])
            rule = pr_dict[self.product_id.id][pricelist.id][1]
            rule_id = self.env['product.pricelist.item'].browse(rule)
            res = rule_id.commission_id
        return res

    @api.one
    @api.onchange('product_id', 'quantity')
    def onchange_product_id_sale_commission_pricelist(self):
        commission = self.get_commission_from_pricelist()
        if commission:
            for agent in self.agents:
                agent.update({
                    'commission': commission.id,
                })
