# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade  # pylint: disable=W7936
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "sale_commission", "migrations/13.0.1.0.0/noupdate_changes.xml"
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
        UPDATE account_invoice_line_agent aila
        SET object_id = aml.id
        FROM account_move_line aml
        WHERE aml.old_invoice_line_id = aila.{}
    """
        ).format(sql.Identifier(openupgrade.get_legacy_name("object_id"))),
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
        UPDATE account_invoice_line_agent aila
        SET invoice_id = am.id
        FROM account_move am
        WHERE am.old_invoice_id = aila.{}
    """
        ).format(sql.Identifier(openupgrade.get_legacy_name("invoice_id"))),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_commission_settlement scs
        SET invoice_id = am.id
        FROM account_move am
        WHERE am.old_invoice_id = scs.invoice
        """,
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
        UPDATE sale_commission_settlement_line scsl
        SET invoice_line_id = aml.id
        FROM account_move_line aml
        WHERE aml.old_invoice_line_id = scsl.{}
    """
        ).format(sql.Identifier(openupgrade.get_legacy_name("invoice_line_id"))),
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move am
            SET commission_total = ai.commission_total
            FROM account_invoice ai
            WHERE ai.id = am.old_invoice_id
                AND ai.commission_total IS NOT NULL
                AND ai.commission_total != 0.0
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move_line aml
            SET commission_free = ail.commission_free
            FROM account_invoice_line ail
            WHERE aml.old_invoice_line_id = ail.id AND ail.commission_free
        """,
    )
