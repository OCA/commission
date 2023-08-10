# Copyright 2023 Tecnativa - David Vidal
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

table_renames = [
    ("sale_commission", "commission"),
    ("sale_commission_settlement", "commission_settlement"),
    ("sale_commission_make_invoice", "commission_make_invoice"),
    ("sale_commission_settlement_line", "commission_settlement_line"),
    ("sale_commission_make_settle", "commission_make_settle"),
]
model_renames = [
    ("sale.commission", "commission"),
    ("sale.commission.mixin", "commission.mixin"),
    ("sale.commission.line.mixin", "commission.line.mixin"),
    ("sale.commission.settlement", "commission.settlement"),
    ("sale.commission.make.invoice", "commission.make.invoice"),
    ("sale.commission.settlement.line", "commission.settlement.line"),
    ("sale.commission.make.settle", "commission.make.settle"),
]


def _handle_settlement_line_commission_id(env):
    """On the new version, this field is computed stored, but the compute method
    doesn't resolve correctly the link here (as it's handled in `account_commission`),
    so we pre-create the column and fill it properly according old expected data.
    """
    openupgrade.logged_query(
        env.cr, "ALTER TABLE commission_settlement_line ADD commission_id int4"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE commission_settlement_line csl
        SET commission_id = aila.commission_id
        FROM settlement_agent_line_rel rel
        JOIN account_invoice_line_agent aila ON aila.id = rel.agent_line_id
        WHERE rel.settlement_id = csl.id
        AND csl.commission_id IS NULL
        """,
    )


@openupgrade.migrate(no_version=True)
def migrate(env, version):
    openupgrade.rename_tables(env.cr, table_renames)
    openupgrade.rename_models(env.cr, model_renames)
    _handle_settlement_line_commission_id(env)
