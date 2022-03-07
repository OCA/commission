from odoo import fields, models


class SaleCommission(models.Model):
    _inherit = "sale.commission"

    commission_type = fields.Selection(
        selection_add=[("cat_prod_var", "By category / product / variant")],
        ondelete={"cat_prod_var": "set default"},
    )
    item_ids = fields.One2many("commission.item", "commission_id")
