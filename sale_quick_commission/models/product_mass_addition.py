from odoo import models


class ProductMassAddition(models.AbstractModel):
    _inherit = "product.mass.addition"

    def _complete_quick_line_vals(self, vals, lines_key=""):
        res = super(ProductMassAddition, self)._complete_quick_line_vals(
            vals, lines_key
        )
        if res.get("agent_ids"):
            agents = [
                (0, 0, {"agent_id": agent.id, "commission_id": agent.commission_id.id})
                for agent in self.partner_id.agent_ids
            ]
            res.update({"agent_ids": agents})
        return res
