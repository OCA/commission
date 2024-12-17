from openupgradelib import openupgrade


def recompute_partial_commission_settled(env):
    """
    Recompute field "partial_commission_settled"
    of model "account.partial.reconcile"
    Removed in future versions of the module
    """
    partial_reconcile = env["account.partial.reconcile"]
    if getattr(partial_reconcile, "_compute_partial_commission_settled", False):
        partial_reconcile.search([])._compute_partial_commission_settled()


@openupgrade.migrate()
def migrate(env, version):
    recompute_partial_commission_settled(env)
