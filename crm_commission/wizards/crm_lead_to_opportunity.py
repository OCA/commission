from odoo import models


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner"

    def _convert_handle_partner(self, lead, action, partner_id):
        res = super()._convert_handle_partner(lead, action, partner_id)
        if lead.lead_agent_ids and lead.partner_id:
            existing = lead.partner_id.agent_ids
            new_agents = lead.lead_agent_ids - existing
            if new_agents:
                lead.partner_id.write(
                    {"agent_ids": [(4, agent.id) for agent in new_agents]}
                )
        return res
