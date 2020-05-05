from odoo import models, fields


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agent_type = fields.Selection(
        selection_add=[("rebate", "Rebate agent")])
