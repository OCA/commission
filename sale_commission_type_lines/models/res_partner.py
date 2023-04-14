# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
