# Copyright 2015 Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# Copyright 2024 Nextev Srl <odoo@nextev.it>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("product_id")
    @api.depends("move_id.partner_id")
    def _compute_agent_ids(self):
        return super()._compute_agent_ids()
