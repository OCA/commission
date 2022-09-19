# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SettlementLine(models.Model):
    _inherit = "commission.settlement.line"

    agent_line = fields.Many2many(
        comodel_name="account.invoice.line.agent",
        relation="settlement_agent_line_rel",
        column1="settlement_id",
        column2="agent_line_id",
        required=True,
    )
    invoice_line_id = fields.Many2one(
        comodel_name="account.move.line",
        store=True,
        related="agent_line.object_id",
        string="Source invoice line",
    )

    @api.constrains("settlement_id", "agent_line")
    def _check_company(self):
        for record in self:
            for line in record.agent_line:
                if line.company_id != record.company_id:
                    raise UserError(_("Company must be the same"))
