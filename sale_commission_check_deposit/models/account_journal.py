from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_check_journal = fields.Boolean()
    safety_days = fields.Integer(default=5)
