# Copyright 2026 Moduon Team
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    # Skip computation of commission_total and commission_free
    cr.execute(
        "ALTER TABLE account_move "
        "ADD COLUMN IF NOT EXISTS commission_total numeric DEFAULT 0"
    )
    cr.execute(
        "ALTER TABLE account_move_line "
        "ADD COLUMN IF NOT EXISTS commission_free boolean DEFAULT false"
    )
