# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

renamings = {
    "account.move.line": [("agents", "agent_ids")],
    "account.invoice.line.agent": [
        ("agent", "agent_id"),
        ("commission", "commission_id"),
        ("invoice", "invoice_id"),
    ],
    "res.partner": [
        ("agents", "agent_ids"),
        ("commission", "commission_id"),
        ("settlements", "settlement_ids"),
    ],
    "sale.order.line": [("agents", "agent_ids")],
    "sale.order.line.agent": [("agent", "agent_id"), ("commission", "commission_id")],
    "sale.commission": [("sections", "section_ids")],
    "sale.commission.make.invoice": [
        ("journal", "journal_id"),
        ("product", "product_id"),
        ("settlements", "settlement_ids"),
    ],
    "sale.commission.make.settle": [("agents", "agent_ids")],
    "sale.commission.section": [("commission", "commission_id")],
    "sale.commission.settlement": [("lines", "line_ids"), ("agent", "agent_id")],
    "sale.commission.settlement.line": [
        ("agent", "agent_id"),
        ("commission", "commission_id"),
        ("invoice_line", "invoice_line_id"),
        ("settlement", "settlement_id"),
    ],
}

_column_renames = {
    "account_invoice_line_agent": [("object_id", None), ("invoice_id", None)],
    "sale_commission_settlement_line": [("invoice_line_id", None)],
}

_field_adds = [
    (
        "invoice_line_id",
        "sale.commission.settlement.line",
        "sale_commission_settlement_line",
        "many2one",
        False,
        "sale_commission",
    ),
    (
        "invoice_id",
        "sale.commission.settlement",
        "sale_commission_settlement",
        "many2one",
        False,
        "sale_commission",
    ),
    (
        "commission_total",
        "account.move",
        "account_move",
        "float",
        False,
        "sale_commission",
    ),
    (
        "commission_free",
        "account.move.line",
        "account_move_line",
        "boolean",
        False,
        "sale_commission",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    renamed_fields = []
    for model in renamings:
        for old_field, new_field in renamings[model]:
            renamed_fields.append(
                (model, model.replace(".", "_"), old_field, new_field)
            )
    openupgrade.rename_fields(env, renamed_fields)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.add_fields(env, _field_adds)
