# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

TABLE_RENAMES = [
    ("account_invoice_line_agent", "account_invoice_line_commission"),
    ("sale_order_line_agent", "sale_order_line_commission"),
    ("settlement_agent_line_rel", "settlement_commission_line_rel"),
]

COL_RENAMES = [
    ("settlement_commission_line_rel", [
        ("agent_line_id", "commission_line_id"),
    ]),
]

CONSTRAINT_DROPS = [
    "account_invoice_line_agent_unique_agent",
    "sale_order_line_agent_unique_agent",
]


def rename_tables(cr):
    for src, dst in TABLE_RENAMES:
        cr.execute("ALTER TABLE {src} RENAME TO {dst}".format(
            src=src, dst=dst))

    for tbl, renames in COL_RENAMES:
        for src, dst in renames:
            cr.execute(
                """
                ALTER TABLE {tbl}
                RENAME COLUMN {src} TO {dst}
                """.format(
                    tbl=tbl,
                    src=src,
                    dst=dst,
                ))


def save_relation_data(cr):
    cr.execute(
        """
        CREATE TABLE tmp_mig_agent_commissions AS
          SELECT id as agent_id, commission as commission_id
          FROM res_partner WHERE commission IS NOT NULL
        """)
    cr.execute(
        """ALTER TABLE res_partner DROP COLUMN commission"""
    )


def drop_constraints(cr):
    for name in CONSTRAINT_DROPS:
        cr.execute("DROP CONSTRAINT IF EXISTS {0}".format(name))


def migrate(cr, installed_version):
    rename_tables(cr)
    save_relation_data(cr)
    drop_constraints(cr)
