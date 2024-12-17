from odoo import fields, models


class SaleCommissionSettlement(models.Model):
    _inherit = "sale.commission.settlement"

    show_settlement_dates = fields.Boolean(
        related="company_id.commission_show_settlement_dates"
    )
    settlement_date_to = fields.Date(
        readonly=True,
        string="Invoice date up to",
        help="The invoice date used to create the settlement",
    )
    settlement_date_payment_to = fields.Date(
        readonly=True,
        string="Payment date up to",
        help="The payment date used to create the settlement",
    )
