# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tools.sql import column_exists, create_column


def pre_init_hook(env):
    # Created empty, the applied item isn't computed on the existing agent lines,
    # whose amount can't be recomputed once settled
    for table in ("account_invoice_line_agent", "sale_order_line_agent"):
        for column in ("applied_commission_id", "applied_commission_item_id"):
            if not column_exists(env.cr, table, column):
                create_column(env.cr, table, column, "int4")
