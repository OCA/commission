from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_multi_type_commissions = fields.Boolean("Use Multiple Commission Types", default=False)
    commission_ids = fields.Many2many("sale.commission", string="Commissions")
