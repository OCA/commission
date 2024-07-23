from odoo import fields, models


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    partner_id = fields.Many2one(
        "res.partner",
        related="invoice_line_id.partner_id",
    )
    show_partner_settlement_report = fields.Boolean(
        related="company_id.show_partner_settlement_report",
    )
