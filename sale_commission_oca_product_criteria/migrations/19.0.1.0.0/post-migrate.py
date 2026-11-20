# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # Items applied to every company before, whatever company they held
    cr.execute("UPDATE commission_item SET company_id = NULL")
