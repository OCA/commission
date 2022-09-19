# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResPartner(models.Model):
    """Add some fields related to commissions"""

    _inherit = "res.partner"

    settlement_ids = fields.One2many(
        comodel_name="commission.settlement",
        inverse_name="agent_id",
        readonly=True,
    )
