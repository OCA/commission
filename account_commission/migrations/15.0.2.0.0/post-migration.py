# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Fill new invoice_agent_line_id many2one from the old many2many agent_line
    equivalent table. This table always contain only one record on standard use.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE commission_settlement_line csl
        SET invoice_agent_line_id = agent_line_id
        FROM settlement_agent_line_rel rel
        WHERE rel.settlement_id = csl.id
        """,
    )
