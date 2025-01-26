# Copyright 2025 Luis Mileo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, models


class Iterator:
    def __init__(self, value=0):
        self.value = value

    def next(self):
        self.value += 1
        return self.value


class ReportCommissionSettlementXlsx(models.AbstractModel):
    _name = "report.sale_commission.settlement_xls"
    _inherit = "report.report_xlsx.abstract"
    _description = "XLSX Report to show commission settlements"

    def _generate_headers(self, sheet, row, cols, bold, settlement):
        sheet.write(row, 0, _("Agent"), bold)
        sheet.write(row, 1, _("From"), bold)
        sheet.write(row, 2, _("To"), bold)

        sheet.write(row + 1, 0, settlement.agent_id.display_name, bold)
        sheet.write(row + 1, 1, settlement.date_from.isoformat(), bold)
        sheet.write(row + 1, 2, settlement.date_to.isoformat(), bold)

        sheet.write(row + 3, 0, _("Invoice Date"), bold)
        sheet.write(row + 3, 1, _("Invoice"), bold)
        sheet.write(row + 3, 2, _("Invoice Line"), bold)
        sheet.write(row + 3, 3, _("Amount Invoice"), bold)
        sheet.write(row + 3, 4, _("Commission"), bold)
        sheet.write(row + 3, 5, _("Amount Settled"), bold)

    def _generate_footer(self, workbook, sheet, row, cols, bold, settlement):
        currency_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#FFFFCC",
                "num_format": settlement.currency_id.symbol + "#,##0.00",
            }
        )
        sheet.write(row + 1, 5, settlement.total, currency_format)

    def _adjust_column_width(self, sheet, data, headers):
        """Automatically adjust column widths based on content."""
        for col_num, header in enumerate(headers):
            max_length = len(header)
            for row in data:
                if col_num < len(row):
                    max_length = max(max_length, len(str(row[col_num])))
            sheet.set_column(col_num, col_num, max_length + 2)

    def generate_xlsx_report(self, workbook, data, settlements):
        n_cols = Iterator(-1)
        sheet = workbook.add_worksheet("Commission Settlements")
        bold = workbook.add_format({"bold": True, "bg_color": "#FFFFCC"})
        no_bold = workbook.add_format({"bold": False})
        cols = defaultdict(n_cols.next)

        row = 0
        headers = [
            "Invoice Date",
            "Invoice",
            "Invoice Line",
            "Amount Invoice",
            "Commission",
            "Amount Settled",
        ]
        data_rows = []

        for settlement in settlements:
            # Generate headers
            self._generate_headers(sheet, row, cols, bold, settlement)
            row += 3

            for line in settlement.line_ids:
                row_data = [
                    line.date.isoformat(),
                    line.invoice_line_id.move_id.name,
                    line.invoice_line_id.name,
                    line.invoice_line_id.price_total,
                    line.commission_id.display_name,
                    line.settled_amount,
                ]
                data_rows.append(row_data)
                row += 1
                for col_num, cell_value in enumerate(row_data):
                    if col_num in [
                        3,
                        5,
                    ]:  # Format currency for Amount Invoice and Amount Settled
                        currency_format = workbook.add_format(
                            {
                                "num_format": line.currency_id.symbol + "#,##0.00",
                                "bold": False,
                            }
                        )
                        sheet.write(row, col_num, cell_value, currency_format)
                    else:
                        sheet.write(row, col_num, cell_value, no_bold)

            self._generate_footer(workbook, sheet, row, cols, bold, settlement)
            row += 2

        # Adjust column widths to fit content
        self._adjust_column_width(sheet, data_rows, headers)
