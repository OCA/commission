from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Convert the former `agent_line` m2m relation in `commission.line.mixin` into
    the new `settlement_line_ids` o2m relation."""
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE commission_settlement_line
            SET invoice_agent_line_id = sal_rel.agent_line_id
            FROM (
                SELECT DISTINCT ON (agent_line_id) agent_line_id, settlement_id
                FROM settlement_agent_line_rel
                ORDER BY agent_line_id
            ) AS sal_rel
            WHERE id = sal_rel.settlement_id
        """,
    )
