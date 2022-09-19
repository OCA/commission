# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_cancel(self):
        """Put settlements associated to the invoices in exception."""
        self.mapped("line_ids.settlement_id").write({"state": "except_invoice"})
        return super().button_cancel()

    def action_post(self):
        """Put settlements associated to the invoices in invoiced state."""
        self.mapped("line_ids.settlement_id").write({"state": "invoiced"})
        return super().action_post()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    settlement_id = fields.Many2one(
        comodel_name="commission.settlement",
        help="Settlement that generates this invoice line",
        copy=False,
    )

    def _copy_data_extend_business_fields(self, values):
        """
        We don't want to loose the settlement from the line when reversing the line if
        it was a refund.
        We need to include it, but as we don't want change it everytime, we will add
        the data when a context key is passed
        """
        super()._copy_data_extend_business_fields(values)
        if self.settlement_id and self.env.context.get("include_settlement", False):
            values["settlement_id"] = self.settlement_id.id
        return
