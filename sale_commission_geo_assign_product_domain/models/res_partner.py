# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    commission_geo_group_ids = fields.One2many(
        comodel_name="res.partner.commission.group",
        inverse_name="partner_id",
    )

    @api.onchange("commission_type")
    def _onchange_commission_type(self):
        if self.commission_type == "product_restricted":
            self.write(
                {
                    "agent_country_ids": False,
                    "agent_state_ids": False,
                    "agent_zip_from": False,
                    "agent_zip_to": False,
                }
            )
