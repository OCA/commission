from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["account.invoice.line.agent"].search(
        [
            ("settled", "=", True),
            ("commission_id.payment_amount_type", "=", "paid"),
        ]
    )._compute_settled()
