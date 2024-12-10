from openupgradelib import openupgrade


def recompute_partial_commission_settled(env):
    """
    Recompute field "partial_commission_settled"
    of model "account.partial.reconcile"
    """
    env["account.partial.reconcile"].search([])._compute_partial_commission_settled()


@openupgrade.migrate()
def migrate(env, version):
    recompute_partial_commission_settled(env)
