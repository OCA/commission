# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizardGeoAssign(models.TransientModel):
    _name = "wizard.geo.assign.partner"
    _description = "Wizard Geo Assign Partner"

    check_existing_agents = fields.Boolean(
        string="Check Existing Agents",
        help="If checked, partners with already assigned agents will be "
        "blocked. Otherwise, found agents will be added",
        default=True,
    )
    replace_existing_agents = fields.Boolean(string="Replace Existing Agents")

    @api.onchange("replace_existing_agents")
    def _onchange_replace_existing_agents(self):
        self.check_existing_agents = not self.replace_existing_agents

    def geo_assign_partner(self):
        self.ensure_one()
        partner_model = self.env["res.partner"]
        agents = partner_model.search([("agent", "=", True)])
        if not agents:
            raise UserError(_("No agents found in the system"))
        partners = partner_model.browse(self.env.context.get("active_ids"))
        for partner in partners:
            if partner.no_geo_assign_update:
                raise UserError(
                    _("Partner %s is not allowed to be updated through geo assignation")
                    % partner.display_name
                )
            if len(partner.agent_ids) > 0 and self.check_existing_agents:
                raise UserError(
                    _(
                        "Partner %s already has agents. You should remove them"
                        " or deselect 'Do not add new agents if agents are already assigned'"
                    )
                    % partner.display_name
                )

            if self.replace_existing_agents:
                partner.write(
                    {
                        "agent_ids": [(5, 0, 0)],
                    }
                )
                if "commission_item_agent_ids" in partner._fields:
                    # compatibility with 'sale_commission_product_criteria_domain'
                    partner.commission_item_agent_ids.unlink()

            for agent in agents:
                self.update_partner_data(partner, agent)

    @api.model
    def update_partner_data(self, partner, agent):
        if agent.is_assignable(partner):
            partner.agent_ids = [(4, agent.id)]
