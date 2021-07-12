# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleCommissionSettlement(models.Model):
    _inherit = "sale.commission.settlement"

    def _get_invoice_partner(self):
        agent = self[0].agent_id
        if agent.delegated_agent_id:
            return agent.delegated_agent_id
        return super(SaleCommissionSettlement, self)._get_invoice_partner()

    def _post_process_line(self, line_form):
        if self.agent_id.delegated_agent_id:
            line_form.name += "\n" + _("Agent: %s") % self.agent_id.display_name
        super()._post_process_line(line_form)
