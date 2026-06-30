# Copyright 2026 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    @api.depends("object_id.quantity", "invoice_date")
    def _compute_amount(self):
        # ``product_fixed`` amounts depend on the invoiced quantity and on the
        # invoice date (for quantity tiers and validity windows), which are not
        # part of the base dependencies. Add them so the commission amount is
        # recomputed when they change.
        return super()._compute_amount()


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        self._check_product_fixed_commission()
        return super().action_post()

    def _check_product_fixed_commission(self):
        """Block posting when a product/agent fixed commission is not defined.

        For every commission of type ``product_fixed`` assigned on an invoice
        line, the corresponding product must have an amount configured in the
        commission. Otherwise the commission cannot be determined and the
        invoice must not be posted.
        """
        missing = []
        for move in self:
            if move.move_type[:3] != "out":
                continue
            for line in move.invoice_line_ids:
                if line.commission_free:
                    continue
                if not line.product_id:
                    continue
                for agent in line.agent_ids:
                    commission = agent.commission_id
                    if commission.commission_type != "product_fixed":
                        continue
                    # Use the same effective date as ``_get_commission_amount``
                    # (the agent line's own ``invoice_date``) so the guard and
                    # the amount computation never disagree on line validity.
                    date = agent.invoice_date or fields.Date.context_today(agent)
                    if commission._get_product_fixed_line(
                        line.product_id, date, line.quantity
                    ):
                        continue
                    missing.append(
                        self.env._(
                            "%(agent)s / %(product)s (commission: %(commission)s)",
                            agent=agent.agent_id.display_name,
                            product=line.product_id.display_name,
                            commission=commission.display_name,
                        )
                    )
        if missing:
            raise ValidationError(
                self.env._(
                    "No fixed commission amount is defined for the following "
                    "agent / product combinations:\n%s",
                    "\n".join(f"- {m}" for m in missing),
                )
            )
