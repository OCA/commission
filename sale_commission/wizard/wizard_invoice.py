# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Inform??ticos (<http://www.pexego.es>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp import exceptions


class settled_invoice_wizard(models.TransientModel):
    """settled.invoice.wizard"""

    _name = 'settled.invoice.wizard'

    journal_id = fields.Many2one('account.journal', 'Target journal',
                                 required=True, select=1)
    product_id = fields.Many2one('product.product', 'Product for account',
                                 required=True, select=1)

    @api.multi
    def create_invoice(self):
        settlement_obj = self.env['settlement']
        self.ensure_one()
        res = settlement_obj.action_invoice_create(self.journal_id,
                                                   self.product_id)
        invoice_ids = res.values()
        if not invoice_ids[0]:
            raise exceptions.Warning(_('No Invoices were created'))
        # change state settlement
        settlement = settlement_obj.browse(self.env.context['active_ids'])
        settlement.state = 'invoiced'
        action = self.env.ref('account.action_invoice_tree2')
        domain = "[('id','in', [{}])]".format(
            ','.join(map(str, invoice_ids[0])))
        vals = {
            'domain': domain,
            'name': action.name,
            'view_mode': action.view_mode,
            'view_type': action.view_type,
            'views': [],
            'res_model': action.res_model,
            'type': action.type,
            }
        return vals
