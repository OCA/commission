from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_check_journal = fields.Boolean()
    safety_days = fields.Integer(
        string="Safety days for commission",
        help="Days after expiration date for commission settlement",
        default=5,
    )
