from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    commission_ids = fields.Many2many("sale.commission", string="Commissions")
