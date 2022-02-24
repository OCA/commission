from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_multi_type_commissions = fields.Boolean("Use Multiple Commission Types", default=False)
    commission_ids = fields.Many2many("sale.commission", string="Commissions", domain=[('commission_type', '=', 'cat_prod_var')])

    @api.onchange("use_multi_type_commissions")
    def onchange_use_multi_type_commissions(self):
        if self.use_multi_type_commissions:
            self.commission_id = False
        else:
            self.commission_ids = [(5, 0, 0)]
