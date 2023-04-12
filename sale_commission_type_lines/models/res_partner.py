from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_multi_type_commissions = fields.Boolean("Use Multiple Commission Types")
    commission_ids = fields.One2many(
        "agent.commission",
        "agent_id",
        string="Commissions",
    )
    customer_ids_count = fields.Integer(compute="_compute_customer_ids_count")
    agent_line_ids = fields.One2many(
        "agent.customer.relation",
        "customer_id",
        string="Agent Lines",
        help="Replacement for agent_ids",
    )
    agent_ids = fields.Many2many(
        "res.partner", compute="_compute_agent_ids", store=True
    )

    def write(self, vals):
        self.remove_single_commission_records(vals)
        res = super(ResPartner, self).write(vals)
        self.single_commission_updates()
        self.check_agent_lines()
        return res

    def remove_single_commission_records(self, vals):
        for rec in self:
            if (
                rec.agent
                and vals.get("use_multi_type_commissions")
                and vals["use_multi_type_commissions"]
            ):
                rels = self.env["agent.commission"].search([("agent_id", "=", rec.id)])
                rels.unlink()

    def single_commission_updates(self):
        for rec in self:
            if rec.agent and not rec.use_multi_type_commissions and rec.commission_id:
                exists = False
                rels = self.env["agent.commission"].search([("agent_id", "=", rec.id)])
                for rel in rels:
                    if rel.commission_id.id != rec.commission_id.id:
                        rel.unlink()
                    else:
                        exists = True
                if not exists:
                    self.env["agent.commission"].create(
                        {
                            "agent_id": rec.id,
                            "commission_id": rec.commission_id.id,
                        }
                    )

    def check_agent_lines(self):
        for rec in self:
            agents = [r.agent_id for r in rec.agent_line_ids]
            dupes = {x.name for x in agents if agents.count(x) > 1}
            if dupes:
                raise ValidationError(
                    _("Agent %s already present in the table." % dupes)
                )

    @api.depends("agent_line_ids")
    def _compute_agent_ids(self):
        # required for compatibility with sale_commission_agent_restrict
        for r in self:
            r.agent_ids = [(6, 0, r.agent_line_ids.mapped("agent_id").ids)]

    def _compute_customer_ids_count(self):
        for r in self:
            acr_recs = self.env["agent.customer.relation"].search(
                [("agent_id", "=", r.id)]
            )
            r.customer_ids_count = len(acr_recs)

    @api.onchange("use_multi_type_commissions")
    def onchange_use_multi_type_commissions(self):
        if self.use_multi_type_commissions:
            self.commission_id = False
        else:
            self.commission_ids = [(5, 0, 0)]

    def action_view_agent_customers(self):
        self.ensure_one()
        acr_recs = self.env["agent.customer.relation"].search(
            [("agent_id", "=", self.id)]
        )
        action = {
            "name": _("Customers of %s", self.name),
            "res_model": "agent.customer.relation",
            "view_mode": "tree,form",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", acr_recs.ids)],
        }
        return action

    @api.model
    def create(self, vals):
        if self.env.user.partner_id.agent:
            vals["agent_line_ids"] = [
                (
                    0,
                    0,
                    {"agent_id": self.env.user.partner_id.id, "customer_id": self.id},
                )
            ]
        res = super(ResPartner, self).create(vals)
        return res
