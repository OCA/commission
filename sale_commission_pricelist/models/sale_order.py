# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2020 ElvenStudio - Vincenzo Terzulli <v.terzulli@elvenstudio.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def recompute_lines_agents(self):
        ctx = {'partner_id': self.partner_id.id}
        for record in self:
            for line in record.order_line.with_context(ctx):
                # delete all existing commissions
                line.agents.unlink()

                # set default values for agent commission
                default_agents = line._default_agents()
                line.write({'agents': default_agents})

                # set commission from pricelist
                line.onchange_product_id_sale_commission_pricelist()
