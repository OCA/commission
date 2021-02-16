from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        rule = env.ref("sale_commission.sale_order_line_analysis_see_all")
        rule.model_id = env.ref(
            "sale_commission.model_sale_order_commission_analysis_report").id
