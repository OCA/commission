# Copyright 2021 KMEE - Luis Felipe Mileo
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
            if not self and vals.get("invoice_id"):
                invoice = self.env["account.invoice"].browse(vals["invoice_id"])

            if invoice.partner_id and invoice.team_id:
                return self._prepare_agents_team_vals_partner(
                    invoice.partner_id, invoice.team_id
                )
        return res
