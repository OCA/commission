from openupgradelib import openupgrade

PREDEFINED_RULES = [
    "base.res_partner_rule_private_employee",
    "base.res_partner_rule_private_group",
]


def reset_predefined_rules_to_active(env):
    """
    Set rules that were deactivated by the previous version
    of the module back to active
    """
    for rule_xml_id in PREDEFINED_RULES:
        env.ref(rule_xml_id).active = True


def remove_view_with_removed_field(env):
    """
    This view had nothing else in it but the removed field
    so it should be safe to remove
    """
    view = env.ref(
        "sale_commission_agent_restrict.view_order_form_partner_domain_inherit",
        raise_if_not_found=False,
    )
    if view:
        view.unlink()


@openupgrade.migrate()
def migrate(env, version):
    reset_predefined_rules_to_active(env)
    remove_view_with_removed_field(env)
