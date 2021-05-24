# Copyright 2014-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models


class SaleCommissionMakeSettle(models.TransientModel):
    _name = "sale.commission.make.settle"
    _description = "Wizard for settling commissions in invoices"

    date_to = fields.Date("Up to", required=True, default=fields.Date.today())
    agent_ids = fields.Many2many(
        comodel_name="res.partner", domain="[('agent', '=', True)]"
    )

    def _get_period_start(self, agent, date_to):
        if agent.settlement == "monthly":
            return date(month=date_to.month, year=date_to.year, day=1)
        elif agent.settlement == "quaterly":
            # Get first month of the date quarter
            month = (date_to.month - 1) // 3 * 3 + 1
            return date(month=month, year=date_to.year, day=1)
        elif agent.settlement == "semi":
            if date_to.month > 6:
                return date(month=7, year=date_to.year, day=1)
            else:
                return date(month=1, year=date_to.year, day=1)
        elif agent.settlement == "annual":
            return date(month=1, year=date_to.year, day=1)

    def _get_next_period_date(self, agent, current_date):
        if agent.settlement == "monthly":
            return current_date + relativedelta(months=1)
        elif agent.settlement == "quaterly":
            return current_date + relativedelta(months=3)
        elif agent.settlement == "semi":
            return current_date + relativedelta(months=6)
        elif agent.settlement == "annual":
            return current_date + relativedelta(years=1)

    def _get_settlement(self, agent, company, sett_from, sett_to):
        return self.env["sale.commission.settlement"].search(
            [
                ("agent_id", "=", agent.id),
                ("date_from", "=", sett_from),
                ("date_to", "=", sett_to),
                ("company_id", "=", company.id),
                ("state", "=", "settled"),
            ],
            limit=1,
        )

    def _prepare_settlement_vals(self, agent, company, sett_from, sett_to):
        return {
            "agent_id": agent.id,
            "date_from": sett_from,
            "date_to": sett_to,
            "company_id": company.id,
        }

    def action_settle(self):
        self.ensure_one()
        agent_line_obj = self.env["account.invoice.line.agent"]
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
            # Get non settled invoices
            agent_lines = agent_line_obj.search(
                [
                    ("invoice_date", "<", date_to_agent),
                    ("agent_id", "=", agent.id),
                    ("settled", "=", False),
                ],
                order="invoice_date",
            )
            for company in agent_lines.mapped("company_id"):
                agent_lines_company = agent_lines.filtered(
                    lambda r: r.object_id.company_id == company
                )
                pos = 0
                sett_to = date(year=1900, month=1, day=1)
                while pos < len(agent_lines_company):
                    line = agent_lines_company[pos]
                    pos += 1
                    if line._skip_settlement():
                        continue
                    if line.invoice_date > sett_to:
                        sett_from = self._get_period_start(agent, line.invoice_date)
                        sett_to = (
                            self._get_next_period_date(
                                agent,
                                sett_from,
                            )
                            - timedelta(days=1)
                        )
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
                            "agent_line": [(6, 0, [line.id])],
                        }
                    )
        # go to results
        if len(settlement_ids):
            return {
                "name": _("Created Settlements"),
                "type": "ir.actions.act_window",
                "views": [[False, "list"], [False, "form"]],
                "res_model": "sale.commission.settlement",
                "domain": [["id", "in", settlement_ids]],
            }
