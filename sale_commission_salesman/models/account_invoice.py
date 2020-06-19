# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _prepare_agents_vals(self, vals=None):
        """Add salesman agent if configured so and no other commission
        already populated.
        """
        res = super()._prepare_agents_vals(vals=vals)
        if not res:
            partner = self.invoice_id.user_id.partner_id
            if not self and vals.get("invoice_id"):
                invoice = self.env["account.invoice"].browse(vals["invoice_id"])
                partner = invoice.user_id.partner_id
            if partner.agent and partner.salesman_as_agent:
                res = [
                    (0, 0, {
                        'agent': partner.id,
                        'commission': partner.commission.id,
                    }),
                ]
        return res
