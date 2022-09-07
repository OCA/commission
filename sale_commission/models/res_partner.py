from odoo import fields, models


class ResPartner(models.Model):
    """Add some fields related to commissions"""

    _inherit = "res.partner"

    settlement_ids = fields.One2many(
        comodel_name="sale.commission.settlement",
        inverse_name="agent_id",
        readonly=True,
    )
