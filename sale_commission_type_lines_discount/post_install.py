# © 2023 ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api
from odoo.tests.common import Form


def enable_discounts(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        config = Form(env["res.config.settings"])
        config.group_discount_per_so_line = True
        config = config.save()
        config.execute()
    return
