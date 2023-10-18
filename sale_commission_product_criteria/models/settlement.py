# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SettlementLine(models.Model):
    _inherit = "commission.settlement.line"
