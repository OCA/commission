# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2020 ElvenStudio - Vincenzo Terzulli <v.terzulli@elvenstudio.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import api, models

import logging
_log = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def recompute_lines_agents(self):
        _log.info("Recomputing invoices agent commissions...")
        for record in self:
            old_value = record.commission_total

            ctx = {'partner_id': record.partner_id.id}
            for line in record.invoice_line.with_context(ctx):
                # delete all existing commissions
                line.agents.unlink()

                # set default values for agent commission
                default_agents = line._default_agents()
                line.write({'agents': default_agents})

                # set commission from pricelist
                line.onchange_product_id_sale_commission_pricelist()

            new_value = record.commission_total

            _log.info("Processed %s: %f => %f" % (record.name, old_value, new_value))
