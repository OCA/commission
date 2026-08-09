from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    lead_agent_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="crm_lead_agent_rel",
        column1="lead_id",
        column2="agent_id",
        string="Agentes",
        domain=[("agent", "=", True)],
        help="Agentes comissionados para este lead. "
        "Serão propagados ao cliente na conversão.",
    )

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        vals = super()._prepare_customer_values(
            partner_name, is_company=is_company, parent_id=parent_id
        )
        if self.lead_agent_ids:
            vals["agent_ids"] = [(6, 0, self.lead_agent_ids.ids)]
        return vals
