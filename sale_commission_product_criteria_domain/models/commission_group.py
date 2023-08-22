# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, exceptions, fields, models


class CommissionItemsGroup(models.Model):
    _name = "commission.items.group"
    _description = "Commission Items Group"
    _sql_constraints = [
        (
            "unique_cig_name",
            "UNIQUE(name)",
            "Commission items group with such name already exists. "
            "Name must be unique.",
        )
    ]

    name = fields.Char(required=True)
    commission_ids = fields.Many2many(
        "sale.commission",
        compute="_compute_commission_ids",
        domain=[("commission_type", "=", "product_restricted")],
        readonly=True,
        store=True,
    )
    item_ids = fields.One2many(
        "commission.item", "group_id", string="Items", readonly=True
    )
    agents_count = fields.Integer(compute="_compute_agents_count")

    @api.depends("item_ids")
    def _compute_commission_ids(self):
        for rec in self:
            rec.commission_ids = [(6, 0, rec.item_ids.mapped("commission_id").ids)]

    def unlink(self):
        if self.item_ids:
            raise exceptions.ValidationError(
                _(
                    "You can not delete this commission group since "
                    "there is related to it commission items."
                )
            )
        return super().unlink()

    def _compute_agents_count(self):
        res_partner_obj = self.env["res.partner"]
        for rec in self:
            self.agents_count = res_partner_obj.search_count(
                [
                    ("agent", "=", True),
                    ("allowed_commission_group_ids", "in", rec.ids),
                ]
            )

    def action_open_related_agents(self):
        agent_ids = self.env["res.partner"].search(
            [
                ("agent", "=", True),
                ("allowed_commission_group_ids", "in", self.ids),
            ]
        )
        return {
            "name": _("Commission Group Agents"),
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "res.partner",
            "context": self.env.context,
            "domain": [("id", "in", agent_ids.ids)],
        }
