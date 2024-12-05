# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Commission(models.Model):
    _inherit = "commission"

    invoice_state = fields.Selection(
        [
            ("open", "Invoice Based"),
            ("paid", "Payment Based"),
            ("paid_date", "Payment Date Based"),
        ],
        string="Invoice Status",
        default="open",
        help="Select the invoice status for settling the commissions:\n"
        "* 'Invoice Based': Commissions are settled when the invoice is issued.\n"
        "* 'Payment Based': Commissions are settled when the invoice is paid (or refunded)\n."
        "* 'Payment Date Based': Commissions are settled based on the payment date.",
    )
