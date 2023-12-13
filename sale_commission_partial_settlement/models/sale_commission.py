# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleCommission(models.Model):
    _inherit = "sale.commission"

    payment_amount_type = fields.Selection(
        [("full", "Full amount"), ("paid", "Paid amount")],
        string="Payment amount type",
        required=True,
        default="full",
    )
