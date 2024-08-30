from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_sql_constraint_safely(
        env,
        "sale_commission_product_criteria_domain",
        "commission_item_agent",
        "commission_item_unique_agent",
    )
