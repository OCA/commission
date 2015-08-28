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
]

COL_RENAMES = [
    # Columns to rename ("Table", [("col_before", "col_after")])
]

CONSTRAINT_DROPS = [
    # Constraints to drop ("Table", ["constraint_name"])
    ("account_invoice_line", ["account_invoice_line_agent_unique_agent"]),
    ("sale_order_line", ["sale_order_line_agent_unique_agent"]),
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
    cr.execute(
        """
        CREATE TABLE tmp_mig_settlement_line_rel AS
          SELECT agent_line_id, settlement_id
          FROM settlement_agent_line_rel
        """
    )


def drop_constraints(cr):
    for table, names in CONSTRAINT_DROPS:
        for name in names:
            cr.execute(
                """
                ALTER TABLE {table}
                DROP CONSTRAINT IF EXISTS {name}
                """.format(table=table,
                           name=name))

def update_model_data(cr):
    cr.executemany(
        """
        UPDATE ir_model_data
        SET name = %(name)s
        WHERE name = %(oldname)s
        """,
        [{"oldname": "invoice_line_agent_tree",
          "name":"invoice_line_commission_tree"},
         {"oldname": "invoice_line_form_agent",
          "name": "invoice_line_form_commission"},
         {"oldname": "invoice_form_agent",
          "name": "invoice_form_commission"},
        ])


def migrate(cr, installed_version):
    rename_tables(cr)
    update_model_data(cr)
    save_relation_data(cr)
    drop_constraints(cr)
