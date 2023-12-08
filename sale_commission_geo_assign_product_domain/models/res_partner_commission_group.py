# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerCommissionGroup(models.Model):
    _name = "res.partner.commission.group"
    _description = "Partner Commission Groups by Geolocation"

    partner_id = fields.Many2one("res.partner", ondelete="cascade", required=True)
    country_ids = fields.Many2many("res.country", string="Country")
    state_ids = fields.Many2many("res.country.state", string="State")
    zip_from = fields.Char("Zip From", help="ZIP range where this agent operates")
    zip_to = fields.Char("Zip To", help="ZIP range where this agent operates")

    commission_group_ids = fields.Many2many(
        "commission.items.group",
        required=True,
        domain="[('id', 'in', allowed_commission_group_ids)]",
    )

    allowed_commission_group_ids = fields.Many2many(
        related="partner_id.allowed_commission_group_ids"
    )

    def is_assignable(self, partner):
        # Check if line (self) is assignable to 'partner'
        self.ensure_one()
        if (
            not self.country_ids
            and not self.state_ids
            and not self.zip_from
            and not self.zip_to
        ):
            # if no criteria set on agent, agent is excluded
            return False
        if self.country_ids and partner.country_id not in self.country_ids:
            return False
        if self.state_ids and partner.state_id not in self.state_ids:
            return False
        if self.zip_from and (partner.zip or "").upper() < self.zip_from.upper():
            return False
        if self.zip_to and (partner.zip or "").upper() > self.zip_to.upper():
            return False
        return True
