from odoo import models


class Invoice(models.Model):
    _inherit = "account.invoice"

    def invoice_validate(self):
        res = super(Invoice, self).invoice_validate()
        # super sets them to invoiced
        self.env['sale.commission.settlement'].search(
            [('invoice', 'in', self.ids)]
        )._compute_state()
        return res
