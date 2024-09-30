from odoo import models


class ProductMassAddition(models.AbstractModel):
    _inherit = "product.mass.addition"

    def _complete_quick_line_vals(self, vals, lines_key=""):
        res = super(ProductMassAddition, self)._complete_quick_line_vals(
            vals, lines_key
        )
        res.pop("agent_ids", None)
        return res
