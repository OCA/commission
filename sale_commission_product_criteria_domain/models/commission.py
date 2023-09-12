# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, exceptions, fields, models


class SaleCommission(models.Model):
    _inherit = "sale.commission"

    commission_type = fields.Selection(
        selection_add=[("product_restricted", "Product criteria (with restrictions)")],
        ondelete={"product_restricted": "set default"},
    )


class CommissionItem(models.Model):
    _inherit = "commission.item"

    commission_id = fields.Many2one(
        "sale.commission",
        string="Commission Type",
        domain=[("commission_type", "in", ["product", "product_restricted"])],
        required=True,
    )
    sale_commission_type = fields.Selection(
        related="commission_id.commission_type", readonly=True
    )
    group_id = fields.Many2one(
        "commission.items.group",
        ondelete="restrict",
    )

    def write(self, values):
        res = super().write(values)
        if self.group_id and not self.group_id.commission_ids.ids:
            self.group_id.commission_ids = [(6, 0, self.commission_id.ids)]
        if self.commission_id.commission_type != "product_restricted" and self.group_id:
            self.group_id = False
        return res


class CommissionItemAgent(models.Model):
    _name = "commission.item.agent"
    _description = "Commission Item Agent"

    _sql_constraints = [
        (
            "commission_item_unique_agent",
            "UNIQUE(partner_id, agent_id)",
            "You can only add one time each agent into Commission "
            "Items Groups Restrictions table.",
        )
    ]

    partner_agent_ids = fields.Many2many(related="partner_id.agent_ids")
    agent_group_ids = fields.Many2many(
        "commission.items.group", compute="_compute_agent_group_ids"
    )
    agent_id = fields.Many2one(
        "res.partner", domain='[("id", "in", partner_agent_ids)]', required=True
    )
    partner_id = fields.Many2one(
        "res.partner", domain=[("agent", "=", False)], required=True
    )
    group_ids = fields.Many2many(
        "commission.items.group",
        domain="[('id', 'in', agent_group_ids)]",
        string="Commission Items Groups Restrictions",
        required=True,
    )

    @api.depends("agent_id")
    def _compute_agent_group_ids(self):
        for rec in self:
            if rec.agent_id.allowed_commission_group_ids:
                dom = ("group_id", "in", rec.agent_id.allowed_commission_group_ids.ids)
            else:
                dom = ("group_id", "!=", False)
            items = self.env["commission.item"].search(
                [("commission_id", "=", rec.agent_id.commission_id.id), dom]
            )
            rec.agent_group_ids = [(6, 0, items.mapped("group_id").ids)]

    @api.constrains("group_ids", "agent_id", "partner_id")
    def _constraint_commission_item_agent_ids(self):
        for cia in self:
            if not cia.group_ids:
                raise exceptions.ValidationError(
                    _("At least one group for each restriction must be selected.")
                )
