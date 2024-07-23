from odoo import api, fields, models


class SaleCommissionSettlement(models.Model):
    _inherit = "sale.commission.settlement"

    showable_line_ids = fields.Many2many(
        "sale.commission.settlement.line",
        compute="_compute_showable_line_ids",
    )
    show_partner_settlement_report = fields.Boolean(
        related="company_id.show_partner_settlement_report",
    )

    @api.depends("line_ids", "line_ids.settled_amount")
    def _compute_showable_line_ids(self):
        for record in self:
            lines = record.line_ids
            if record.company_id.settlement_skip_zero_amount_lines:
                lines = lines.filtered(lambda line: line.settled_amount)
            record.showable_line_ids = lines
