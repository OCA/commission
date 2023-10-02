# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class CommissionSettlement(models.Model):
    _inherit = "commission.settlement"

    def mark_as_invoiced(self):
        self.write({"state": "invoiced"})
