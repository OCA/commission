from odoo import fields, models


class AgentCustomerRel(models.Model):
    _name = "agent.customer.relation"
    _description = "Agent Customer Relation"

    agent_id = fields.Many2one(
        "res.partner", "Agent", domain=[("agent", "=", True)], required=True
    )
    customer_id = fields.Many2one("res.partner", "Customer")
    customer_country_id = fields.Many2one(
        "res.country", related="customer_id.country_id"
    )
    customer_state_id = fields.Many2one(
        "res.country.state", related="customer_id.state_id"
    )
    customer_city = fields.Char(related="customer_id.city")
    customer_zip = fields.Char(related="customer_id.zip")
