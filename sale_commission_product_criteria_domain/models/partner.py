# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
import json

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    apply_commission_restrictions = fields.Boolean("Apply Restrictions")
    commission_item_agent_ids = fields.One2many(
        "commission.item.agent", "partner_id", string="Commission Items Groups"
    )
    allowed_commission_group_ids = fields.Many2many(
        "commission.items.group", help="Related only to agents"
    )
    allowed_commission_group_ids_domain = fields.Char(
        compute="_compute_allowed_commission_group_ids_domain",
        readonly=True,
        store=False,
    )
    commission_type = fields.Selection(related="commission_id.commission_type")

    @api.depends("commission_id")
    def _compute_allowed_commission_group_ids_domain(self):
        for rec in self:
            if rec.agent:
                allowed_group_ids = rec.commission_id.filtered(
                    lambda x: x.commission_type == "product_restricted"
                ).item_ids.mapped("group_id")
                rec.allowed_commission_group_ids_domain = json.dumps(
                    [("id", "in", allowed_group_ids.ids)]
                )
            else:
                rec.allowed_commission_group_ids_domain = False

    @api.onchange("agent_ids")
    def _onchange_agent_ids(self):
        for rec in self:
            exiting_agents = rec.commission_item_agent_ids.mapped("agent_id")
            to_create = [
                {"partner_id": rec._origin.id, "agent_id": x._origin.id}
                for x in rec.agent_ids.filtered(
                    lambda x: x.commission_id.commission_type == "product_restricted"
                )
                if x not in exiting_agents.ids
            ]
            to_delete = rec.commission_item_agent_ids.filtered(
                lambda x: x.agent_id.id in (exiting_agents - rec.agent_ids).ids
            )
            if to_delete:
                rec.update(
                    {"commission_item_agent_ids": [(2, dl.id, 0) for dl in to_delete]}
                )
            if to_create:
                rec.update(
                    {"commission_item_agent_ids": [(0, 0, line) for line in to_create]}
                )

    def write(self, vals):
        res = super().write(vals)
        if (
            self.commission_id.commission_type != "product_restricted"
            and self.allowed_commission_group_ids
        ):
            self.allowed_commission_group_ids = False
        return res
