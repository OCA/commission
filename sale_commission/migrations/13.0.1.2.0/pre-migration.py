from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.ref("sale_commission.view_res_partner_filter").unlink()
