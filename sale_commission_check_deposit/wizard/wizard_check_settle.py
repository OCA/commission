# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import json
from datetime import date, timedelta

from odoo import models


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    def _get_agent_lines(self, agent, date_to_agent):
        """
        Exclude invoices with checks payment if at least safety days
        haven't passed since expiration date set on check deposit.
        """
        agent_lines = super()._get_agent_lines(agent, date_to_agent)
        for line in agent_lines.filtered(
            lambda r: r.commission_id.invoice_state == "paid"
            and r.invoice_id.invoice_payments_widget != "false"
        ):
            if not self.get_move_ids(line.invoice_id.invoice_payments_widget):
                agent_lines -= line
        return agent_lines

    def get_move_ids(self, payments_widget):
        move_dict = json.loads(payments_widget)
        account_move_ids = [content["move_id"] for content in move_dict["content"]]
        move_lines = self.env["account.move.line"].search(
            [
                ("move_id", "in", account_move_ids),
                ("journal_id.is_check_journal", "=", True),
                ("check_deposit_id", "!=", False),
            ]
        )
        return all(
            [
                x.date_maturity + timedelta(days=x.journal_id.safety_days)
                < date.today()
                for x in move_lines
            ]
        )
