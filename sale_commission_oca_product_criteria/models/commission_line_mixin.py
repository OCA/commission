# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class CommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    applied_commission_id = fields.Many2one("commission", readonly=True)
    commission_id = fields.Many2one(
        comodel_name="commission",
        ondelete="restrict",
        required=False,
        compute="_compute_commission_id",
        store=True,
        readonly=False,
        copy=True,
    )

    def _get_commission_company(self):
        """Return the company of the document the line belongs to."""
        return self.object_id.company_id or self.env.company

    def _get_commission_items_domain(
        self, commission, product, quantity=0.0, date=None
    ):
        categ_ids = {}
        categ = product.categ_id
        while categ:
            categ_ids[categ.id] = True
            categ = categ.parent_id
        categ_ids = list(categ_ids)
        domain = [
            ("commission_id", "=", commission.id),
            # A commission is shared by every company while its items are not,
            # so only the items of the company of the document can apply to it.
            ("company_id", "in", [self._get_commission_company().id, False]),
            "|",
            ("product_tmpl_id", "=", False),
            ("product_tmpl_id", "=", product.product_tmpl_id.id),
            "|",
            ("product_id", "=", False),
            ("product_id", "=", product.id),
            "|",
            ("categ_id", "=", False),
            ("categ_id", "in", categ_ids),
            # An item without minimum quantity applies to any quantity, which
            # can even be negative on a refund or on a discount line.
            "|",
            ("min_qty", "=", 0),
            ("min_qty", "<=", quantity),
        ]
        if date:
            domain += [
                "|",
                ("date_start", "=", False),
                ("date_start", "<=", date),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", date),
            ]
        return domain

    def _get_line_uom(self):
        """Return the UoM the line quantity is expressed in.

        Overridden in sale.order.line.agent and account.invoice.line.agent,
        as commission.mixin itself doesn't carry a UoM.
        """
        return self.env["uom.uom"]

    def _get_quantity_in_product_uom(self, product, quantity):
        """Convert the line quantity into the product reference UoM.

        Commission item quantities (min_qty, per unit amounts) are expressed
        in that UoM, the same way pricelist item minimum quantities are.
        """
        line_uom = self._get_line_uom()
        product_uom = product.uom_id
        if product_uom and line_uom and line_uom != product_uom:
            # The conversion is rounded up by default, which would inflate the
            # amount and let a line cross a minimum quantity it doesn't reach.
            return line_uom._compute_quantity(quantity, product_uom, round=False)
        return quantity

    def _get_commission_item(self, commission, product, quantity=0.0, date=None):
        """Select the best matching commission item.

        The model ordering returns the best candidate first: most specific
        applied_on level, then highest min_qty, then most specific category.
        """
        return self.env["commission.item"].search(
            self._get_commission_items_domain(commission, product, quantity, date),
            limit=1,
        )

    def _get_company_date(self, timestamp):
        """Return the date of a UTC timestamp in the timezone of the company.

        Item validity is set as a date, so the stored commission must not
        depend on the timezone of the user recomputing it.
        """
        company_tz = self._get_commission_company().partner_id.tz or "UTC"
        return fields.Datetime.context_timestamp(
            self.with_context(tz=company_tz), timestamp
        ).date()

    def _get_commission_date(self):
        """Return the reference date for commission item matching.

        Overridden in sale.order.line.agent and account.invoice.line.agent
        to use the document date (order date / invoice date).
        """
        return self._get_company_date(fields.Datetime.now())

    def _get_commission_currency(self):
        """Return the currency the commission amount is expressed in.

        Overridden in sale.order.line.agent, which doesn't set the currency
        of its own amount.
        """
        return self.currency_id

    def _convert_amount(self, amount, company, date):
        """Convert an amount into the currency of the commission amount.

        Fixed amounts and product costs are expressed in the currency of a
        company, while the commission amount is stored in the currency of the
        document.
        """
        currency = self._get_commission_currency()
        company_currency = company.currency_id
        if not amount or not currency or currency == company_currency:
            return amount
        return company_currency._convert(amount, currency, company, date)

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        self.ensure_one()
        company = self._get_commission_company()
        quantity = self._get_quantity_in_product_uom(product, quantity)
        date = self._get_commission_date()
        commission_item = self._get_commission_item(commission, product, quantity, date)
        if not commission_item:
            return 0.0
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            cost = product.with_company(company).standard_price * quantity
            subtotal = max([0, subtotal - self._convert_amount(cost, company, date)])
        self.applied_commission_item_id = commission_item
        self.applied_commission_id = commission_item.commission_id
        if commission_item.commission_type == "fixed":
            amount = commission_item.fixed_amount
            if commission_item.per_unit:
                amount *= quantity
            return self._convert_amount(
                amount, commission_item.company_id or company, date
            )
        elif commission_item.commission_type == "percentage":
            return subtotal * (commission_item.percent_amount / 100.0)

    def _get_discount_value(self, commission_item):
        # Will be overridden
        return self.object_id.discount
