from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "account_move_line", "settlement_id"):
        openupgrade.logged_query(
            env.cr,
            """ALTER TABLE account_move_line
               ADD COLUMN settlement_id int""",
        )
        if openupgrade.column_exists(env.cr, "account_move", "settlement_id"):
            openupgrade.logged_query(
                env.cr,
                """UPDATE account_move_line aml
                    SET settlement_id = am.settlement_id
                    FROM account_move am
                    WHERE am.id = aml.move_id
                        AND am.settlement_id IS NOT NULL
                        AND aml.settlement_id IS NULL
                """,
            )
