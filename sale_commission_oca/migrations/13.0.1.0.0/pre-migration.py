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


@openupgrade.migrate()
def migrate(env, version):
    renamed_fields = []
    for model in renamings:
        for old_field, new_field in renamings[model]:
            renamed_fields.append(
                (model, model.replace(".", "_"), old_field, new_field)
            )
    openupgrade.rename_fields(env, renamed_fields)
