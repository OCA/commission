# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleCommissionSettlement(models.Model):
    _inherit = "sale.commission.settlement"

    def _prepare_invoice_header(self, settlement, journal, date=False):
        vals = super()._prepare_invoice_header(settlement, journal, date=date)
        if not settlement.agent.delegated_agent_id:
            return vals
        invoice = self.env["account.invoice"].new(vals)
        invoice.partner_id = settlement.agent.delegated_agent_id
        invoice._onchange_partner_id()
        invoice._onchange_journal_id()
        return invoice._convert_to_write(invoice._cache)

    def _prepare_invoice_line(self, settlement, invoice, product):
        invoice_line_vals = super()._prepare_invoice_line(settlement, invoice, product)
        if settlement.agent.delegated_agent_id:
            invoice_line_vals["name"] += (
                "\n" + _("Agent: %s") % settlement.agent.display_name
            )
        return invoice_line_vals
