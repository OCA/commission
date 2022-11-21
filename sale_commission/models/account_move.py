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

    partner_agent_ids = fields.Many2many(
        string="Agents",
        comodel_name="res.partner",
        compute="_compute_agents",
        search="_search_agents",
    )

    @api.depends("partner_agent_ids", "invoice_line_ids.agent_ids.agent_id")
    def _compute_agents(self):
        for move in self:
            move.partner_agent_ids = [
                (6, 0, move.mapped("invoice_line_ids.agent_ids.agent_id").ids)
            ]

    @api.model
    def _search_agents(self, operator, value):
        ail_agents = self.env["account.invoice.line.agent"].search(
            [("agent_id", operator, value)]
        )
        return [("id", "in", ail_agents.mapped("object_id.move_id").ids)]

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
        self.mapped("line_ids.settlement_id").write({"state": "except_invoice"})
        return super().button_cancel()

    def action_post(self):
        """Put settlements associated to the invoices in invoiced state."""
        self.mapped("line_ids.settlement_id").write({"state": "invoiced"})
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
    is_downpayment = fields.Boolean(default=False)
    settlement_id = fields.Many2one(
        comodel_name="sale.commission.settlement",
        help="Settlement that generates this invoice line",
        copy=False,
    )

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
            if record.sale_line_ids and record.sale_line_ids.is_downpayment:
                # Down payment invoice
                agent_ids = record._prepare_agents_vals_down_payment()
                record.update({"is_downpayment": True, "agent_ids": agent_ids})
            else:
                # Regular invoice
                if not record.commission_free and record.product_id:
                    record.agent_ids = record._prepare_agents_vals_partner(
                        record.move_id.partner_id
                    )

    def _prepare_agents_vals_down_payment(self):
        # Add agent lines with amount > 0 and with total commission amount
        self.sale_line_ids.ensure_one()
        sale_order_id = self.sale_line_ids.order_id
        agent_sol_ids = sale_order_id.order_line.filtered(
            lambda x: x.is_downpayment is False and x.product_id and x.agent_ids
        )
        sol_agents = agent_sol_ids.mapped("agent_ids")
        grouped_agent_ids = sol_agents.read_group(
            fields=["agent_id", "amount"],
            domain=[("amount", ">", 0)],
            groupby=["agent_id"],
        )
        res = []
        for agent_line in grouped_agent_ids:
            res.append(
                (
                    0,
                    0,
                    {
                        "agent_id": agent_line["agent_id"][0],
                        "amount": 0,
                        "downpayment_base_amount": agent_line["amount"],
                    },
                )
            )
        return res

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
        related="invoice_id.invoice_date",
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
    commission_id = fields.Many2one(
        comodel_name="sale.commission",
        ondelete="restrict",
        required=False,
        compute="_compute_commission_id",
        store=True,
        readonly=False,
        copy=True,
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
    downpayment_base_amount = fields.Monetary(
        help="Total agent commission based on Sale Order"
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

    @api.depends("agent_id")
    def _compute_commission_id(self):
        for record in self.filtered(lambda x: not x.object_id.is_downpayment):
            record.commission_id = record.agent_id.commission_id

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        # overriden in order to implement down payment logic
        self.ensure_one()
        if self.object_id.is_downpayment:
            sale_order_id = self.object_id.sale_line_ids.order_id
            ratio = self.object_id.price_total / sale_order_id.amount_total
            return self.downpayment_base_amount * ratio
        if product.commission_free or not commission:
            return 0.0
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        if commission.commission_type == "fixed":
            return subtotal * (commission.fix_qty / 100.0)
        elif commission.commission_type == "section":
            return commission.calculate_section(subtotal)
