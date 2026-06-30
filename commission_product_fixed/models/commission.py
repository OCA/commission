# Copyright 2026 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Commission(models.Model):
    _inherit = "commission"

    commission_type = fields.Selection(
        selection_add=[("product_fixed", "Fixed amount per product")],
        ondelete={"product_fixed": "set default"},
    )
    product_line_ids = fields.One2many(
        comodel_name="commission.product.line",
        inverse_name="commission_id",
        string="Product amounts",
        copy=True,
    )

    def _get_product_fixed_line(self, product, date=None, quantity=0.0):
        """Return the applicable product amount line (or empty).

        Lines are filtered by product, validity dates and minimum quantity.
        The most specific match (highest applicable ``min_qty``) is selected
        explicitly, so the result does not depend on the recordset order.
        """
        self.ensure_one()
        lines = self.product_line_ids.filtered(
            lambda x: x.product_id == product and x.min_qty <= quantity
        )
        if date:
            lines = lines.filtered(
                lambda x: (not x.date_start or x.date_start <= date)
                and (not x.date_end or x.date_end >= date)
            )
        return lines.sorted(key=lambda x: x.min_qty, reverse=True)[:1]


class CommissionProductLine(models.Model):
    _name = "commission.product.line"
    _description = "Fixed commission amount per product"
    _order = "sequence, min_qty desc, id"
    _rec_name = "product_id"

    sequence = fields.Integer(default=10)
    commission_id = fields.Many2one(
        comodel_name="commission",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
    )
    min_qty = fields.Float(
        string="Min. Quantity",
        default=0.0,
        help="The minimum invoiced quantity for this amount to apply. When "
        "several lines match a product, the one with the highest applicable "
        "minimum quantity is used.",
    )
    amount = fields.Monetary(
        string="Commission Amount",
        required=True,
        help="Fixed commission amount granted per unit of the product.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    date_start = fields.Date(
        string="Start Date",
        help="Start date for this amount (inclusive).",
    )
    date_end = fields.Date(
        string="End Date",
        help="End date for this amount (inclusive).",
    )

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for line in self:
            if not line.date_start or not line.date_end:
                continue
            if line.date_start <= line.date_end:
                continue
            raise ValidationError(
                self.env._("The start date cannot be after the end date.")
            )
