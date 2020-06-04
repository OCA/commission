# -*- coding: utf-8 -*-
# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line",

    @api.model
    def _prepare_agents_vals(self):
        """Agents taken from the products (rebates)
           TODO: Allow to change agent in case there are more than one
        """
        self.ensure_one()
        res = super(AccountInvoiceLine, self)._prepare_agents_vals()
        agent = self.sale_line_ids._get_supplierinfos()
        if agent:
            res.append({
                'agent': agent[0].name.id,
                'commission': agent[0].name.commission.id
            })
        return res
