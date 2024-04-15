#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def button_edit_agents(self):
        action = super().button_edit_agents()
        if self.user_has_groups(
            "sale_commission_agent_restrict.group_agent_own_commissions"
        ):
            own_commissions_view = self.env.ref(
                "sale_commission_agent_restrict.view_sale_order_line_tree_mod"
            )
            action["view_id"] = own_commissions_view.id
            # action["views"] has shape [(12, "form"), (34, "tree"), ...]
            new_action_views = []
            for view_id_type in action["views"]:
                if view_id_type[1] == "form":
                    view_id_type = (own_commissions_view.id, "form")
                new_action_views.append(view_id_type)
            action["views"] = new_action_views
        return action
