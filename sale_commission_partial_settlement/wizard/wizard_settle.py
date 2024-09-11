# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, models


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    def action_settle(self):
        partial_res = self.action_settle_partial()
        res = super().action_settle()
        if partial_res and res:
            partial_res["domain"][0][2] += res["domain"][0][2]
            return partial_res
        return res if res else partial_res

    def action_settle_partial(self):
        self.ensure_one()
        settlement_obj = self.env["sale.commission.settlement"]
        settlement_line_obj = self.env["sale.commission.settlement.line"]
        settlement_ids = []

        if self.agent_ids:
            agents = self.agent_ids
        else:
            agents = self.env["res.partner"].search([("agent", "=", True)])
        date_to = self.date_to
        for agent in agents:
            date_to_agent = self._get_period_start(agent, date_to)
            main_agent_line = self.get_partial_agent_lines(agent, date_to_agent)
            (
                partial_agent_lines,
                agent_lines_to_update,
            ) = main_agent_line._partial_commissions(self.date_payment_to)
            for line_id in agent_lines_to_update:
                self.env["account.invoice.line.agent"].browse(line_id).update(
                    agent_lines_to_update[line_id]
                )
            for company in partial_agent_lines.mapped(
                "invoice_line_agent_id.company_id"
            ):
                agent_lines_company = partial_agent_lines.filtered(
                    lambda r: r.invoice_line_agent_id.object_id.company_id == company
                )
                sett_to = date.min
                for line in agent_lines_company:
                    if line.invoice_line_agent_id.invoice_date > sett_to:
                        sett_from = self._get_period_start(
                            agent, line.invoice_line_agent_id.invoice_date
                        )
                        sett_to = self._get_next_period_date(
                            agent,
                            sett_from,
                        ) - relativedelta(days=1)
                        settlement = self._get_settlement(
                            agent, company, sett_from, sett_to
                        )
                        if not settlement:
                            settlement = settlement_obj.create(
                                self._prepare_settlement_vals(
                                    agent, company, sett_from, sett_to
                                )
                            )
                        settlement_ids.append(settlement.id)
                    settlement_line_obj.create(
                        {
                            "settlement_id": settlement.id,
                            "agent_line_partial_ids": [(6, 0, [line.id])],
                            "agent_line": [(6, 0, [line.invoice_line_agent_id.id])],
                        }
                    )
        if len(settlement_ids):
            return {
                "name": _("Created Settlements"),
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "tree,form",
                "res_model": "sale.commission.settlement",
                "domain": [["id", "in", settlement_ids]],
            }

    def _get_agent_lines(self, agent, date_to_agent):
        aila = super()._get_agent_lines(agent, date_to_agent)
        return aila.filtered(lambda x: x.commission_id.payment_amount_type != "paid")

    def get_partial_agent_lines(self, agent, date_to_agent):
        main_agent_line = self.env["account.invoice.line.agent"].search(
            [
                ("invoice_date", "<", date_to_agent),
                ("agent_id", "=", agent.id),
                ("settled", "=", False),
                ("commission_id.payment_amount_type", "=", "paid"),
            ],
            order="invoice_date",
        )
        return main_agent_line
