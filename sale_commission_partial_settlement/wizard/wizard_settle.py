# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, models


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    def _prepare_settlement_vals(self, agent, company, sett_from, sett_to):
        vals = super()._prepare_settlement_vals(agent, company, sett_from, sett_to)
        vals.update(
            {
                "settlement_date_to": self.date_to,
                "settlement_date_payment_to": self.date_payment_to,
            }
        )
        return vals

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
        settlements = settlement_obj.browse()
        agents = self.agent_ids or self.env["res.partner"].search(
            [("agent", "=", True)]
        )
        for agent in agents:
            partial_settlement_lines = self.get_partial_settlement_lines(
                agent, self.date_to, self.date_payment_to
            )
            sett_from = sett_to = date.min
            settlement = None
            for partial in partial_settlement_lines:
                if partial.invoice_date > sett_to:
                    sett_from = self._get_period_start(agent, partial.invoice_date)
                    sett_to = self._get_next_period_date(
                        agent,
                        sett_from,
                    ) - relativedelta(days=1)
                    settlement = self._get_settlement(
                        agent, partial.company_id, sett_from, sett_to
                    )
                if not settlement:
                    settlement = settlement_obj.create(
                        self._prepare_settlement_vals(
                            agent, partial.company_id, sett_from, sett_to
                        )
                    )
                    settlements += settlement
                settlement_line_obj.create(
                    {
                        "settlement_id": settlement.id,
                        "agent_line_partial_ids": [
                            (4, partial.invoice_agent_partial_id.id)
                        ],
                        "agent_line": [(4, partial.invoice_line_agent_id.id)],
                        "settlement_line_partial_ids": [(4, partial.id)],
                    }
                )
        if settlements:
            return {
                "name": _("Created Settlements"),
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "tree,form",
                "res_model": "sale.commission.settlement",
                "domain": [["id", "in", settlements.ids]],
            }

    def _get_agent_lines(self, agent, date_to_agent):
        aila = super()._get_agent_lines(agent, date_to_agent)
        return aila.filtered(lambda x: x.commission_id.payment_amount_type != "paid")

    def get_partial_settlement_lines(self, agent, date_to_agent, date_to_payment):
        partial_to_settle = self.env["sale.commission.settlement.line.partial"].search(
            self.get_partial_settlement_domain(agent, date_to_agent, date_to_payment),
            order="invoice_date",
        )
        return partial_to_settle

    def get_partial_settlement_domain(self, agent, date_to_agent, date_to_payment):
        domain = [
            ("invoice_date", "<", date_to_agent),
            ("agent_id", "=", agent.id),
            ("is_settled", "=", False),
        ]
        if date_to_payment:
            domain.append(("date_maturity", "<", date_to_payment))
        return domain
