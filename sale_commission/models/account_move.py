# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, exceptions, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    commission_total = fields.Float(
        string="Commissions",
        compute="_compute_commission_total",
        store=True,
    )
    settlement_id = fields.Many2one(
        comodel_name="sale.commission.settlement",
        help="Settlement that generates this invoice",
        copy=False,
    )

    @api.depends("line_ids.agent_ids.amount")
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.line_ids:
                record.commission_total += sum(x.amount for x in line.agent_ids)

    def button_cancel(self):
        """Put settlements associated to the invoices in exception
        and check settled lines"""
        if any(self.mapped("invoice_line_ids.any_settled")):
            raise exceptions.ValidationError(
                _("You can't cancel an invoice with settled lines"),
            )
        self.settlement_id.state = "except_invoice"
        return super().button_cancel()

    def action_post(self):
        """Put settlements associated to the invoices in invoiced state."""
        self.settlement_id.state = "invoiced"
        return super().action_post()

    def recompute_lines_agents(self):
        self.mapped("invoice_line_ids").recompute_agents()

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """Inject in this method the needed context for not removing other
        possible context values.
        """
        res = super(AccountMove, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form":
            invoice_xml = etree.XML(res["arch"])
            invoice_line_fields = invoice_xml.xpath("//field[@name='invoice_line_ids']")
            if invoice_line_fields:
                invoice_line_field = invoice_line_fields[0]
                context = invoice_line_field.attrib.get("context", "{}").replace(
                    "{",
                    "{'partner_id': partner_id, ",
                    1,
                )
                invoice_line_field.attrib["context"] = context
                res["arch"] = etree.tostring(invoice_xml)
        return res


class AccountMoveLine(models.Model):
    _inherit = [
        "account.move.line",
        "sale.commission.mixin",
    ]
    _name = "account.move.line"

    agent_ids = fields.One2many(comodel_name="account.invoice.line.agent")
    any_settled = fields.Boolean(compute="_compute_any_settled")

    @api.depends("agent_ids", "agent_ids.settled")
    def _compute_any_settled(self):
        for record in self:
            record.any_settled = any(record.mapped("agent_ids.settled"))

    @api.depends("move_id.partner_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        for record in self.filtered(
            lambda x: x.move_id.partner_id and x.move_id.move_type[:3] == "out"
        ):
            if not record.commission_free and record.product_id:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.move_id.partner_id
                )


class AccountInvoiceLineAgent(models.Model):
    _inherit = "sale.commission.line.mixin"
    _name = "account.invoice.line.agent"
    _description = "Agent detail of commission line in invoice lines"

    object_id = fields.Many2one(comodel_name="account.move.line")
    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name="account.move",
        related="object_id.move_id",
        store=True,
    )
    invoice_date = fields.Date(
        string="Invoice date",
        related="invoice_id.date",
        store=True,
        readonly=True,
    )
    agent_line = fields.Many2many(
        comodel_name="sale.commission.settlement.line",
        relation="settlement_agent_line_rel",
        column1="agent_line_id",
        column2="settlement_id",
        copy=False,
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
        "object_id.price_subtotal",
        "object_id.product_id.commission_free",
        "commission_id",
    )
    def _compute_amount(self):
        for line in self:
            inv_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                inv_line.price_subtotal,
                inv_line.product_id,
                inv_line.quantity,
            )
            # Refunds commissions are negative
            if line.invoice_id.move_type and "refund" in line.invoice_id.move_type:
                line.amount = -line.amount

    @api.depends(
        "agent_line", "agent_line.settlement_id.state", "invoice_id", "invoice_id.state"
    )
    def _compute_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        for line in self:
            line.settled = any(
                x.settlement_id.state != "cancel" for x in line.agent_line
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
        return (
            self.commission_id.invoice_state == "paid"
            and self.invoice_id.payment_state not in ["in_payment", "paid"]
        ) or self.invoice_id.state != "posted"
