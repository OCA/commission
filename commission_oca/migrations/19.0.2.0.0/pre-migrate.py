from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "res.partner",
                env["res.partner"]._table,
                "agent_ids",
                "commission_agent_ids",
            ),
        ],
    )
