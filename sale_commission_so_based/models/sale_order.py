# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
from odoo import _, api, exceptions, fields, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"
    invoice_date = fields.Date(
        compute="_compute_invoice_date",
        store=True,
        readonly=True,
    )
    order_id = fields.Many2one(
        comodel_name="sale.order",
        related="object_id.order_id",
        store=True,
    )
    order_date = fields.Datetime(
        related="order_id.date_order",
        store=True,
        readonly=True,
    )
    settlement_line_ids = fields.One2many(
        comodel_name="commission.settlement.line",
        inverse_name="sale_agent_line_id",
    )
    settled = fields.Boolean(compute="_compute_settled", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        compute="_compute_company",
        store=True,
    )
    currency_id = fields.Many2one(
        related="object_id.currency_id",
        readonly=True,
    )

    @api.depends(
        "settlement_line_ids",
        "settlement_line_ids.settlement_id.state",
        "order_id",
        "order_id.state",
    )
    def _compute_settled(self):
        # TODO: This is a copy of the account.invoice.line.agent method.
        # Should be finished.(look for tests)
        for line in self:
            line.settled = any(
                x.settlement_id.state != "cancel" for x in line.settlement_line_ids
            )

    @api.depends("object_id", "object_id.company_id")
    def _compute_company(self):
        for line in self:
            line.company_id = line.object_id.company_id

    @api.constrains("agent_id", "amount")
    def _check_settle_integrity(self):
        for record in self:
            if any(record.mapped("settled")):
                raise exceptions.ValidationError(
                    _("You can't modify a settled line"),
                )

    def _skip_settlement(self):
        """This function should return False if the commission can be paid.
        :return: bool
        """
        self.ensure_one()
        return self.order_id.state not in ("sale", "done")

    @api.depends("order_id", "order_id.date_order")
    def _compute_invoice_date(self):
        for record in self:
            order_date = record.order_id.date_order
            record.invoice_date = order_date.date() if order_date else False
