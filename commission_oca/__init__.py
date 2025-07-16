from . import models
from . import wizards

from openupgradelib import openupgrade


def _commission_oca_pre_init_hook(env):
    if openupgrade.table_exists(env.cr, "commission"):
        openupgrade.rename_models(
            env.cr,
            [
                ("sale.commission", "commission"),
                ("sale.commission.settlement", "commission.settlement"),
            ],
        )
        openupgrade.rename_tables(
            env.cr,
            [
                ("sale_commission", "commission"),
                ("sale_commission_settlement", "commission_settlement"),
            ],
        )

        modules = [("commission", "commission_oca")]
        openupgrade.update_module_names(env.cr, modules, merge_modules=True)
