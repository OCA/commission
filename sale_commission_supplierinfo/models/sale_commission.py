# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SaleCommission(models.Model):
    _inherit = "sale.commission"

    commission_type = fields.Selection(selection_add=[("supplierinfo", "Supplierinfo")])
