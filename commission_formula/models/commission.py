# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class Commission(models.Model):
    _inherit = "commission"

    commission_type = fields.Selection(
        selection_add=[("formula", "Formula")], ondelete={"formula": "set default"}
    )
    formula = fields.Text(
        default="if line._name == 'sale.order.line':\n"
        "    result = 0\n"
        "if line._name == 'account.move.line':\n"
        "    result = 0\n",
    )
