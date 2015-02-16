# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
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

"""invoice agents"""

from openerp import models, fields, api, _


class invoice_line_agent(models.Model):
    """invoice agents"""

    _name = "invoice.line.agent"

    invoice_line_id = fields.Many2one(
        "account.invoice.line",
        string="Invoice Line",
        required=True,
        ondelete="cascade"
    )

    invoice_id = fields.Many2one(
        "account.invoice",
        string="Invoice",
        related="invoice_line_id.invoice_id"
    )

    invoice_date = fields.Date(
        string="Invoice date",
        related="invoice_id.date_invoice",
        readonly=True
    )

    agent_id = fields.Many2one(
        "sale.agent",
        string="Agent",
        required=True,
        ondelete="cascade"
    )

    commission_id = fields.Many2one(
        "commission",
        string="Applied commission",
        required=True,
        ondelete="cascade",
    )

    settled = fields.Boolean(
        string="Settled",
        readonly=True,
        default=False
    )

    quantity = fields.Float(string="Settled amount", default=0)

    def calculate_commission(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for line_agent in self.browse(cr, uid, ids, context):
            commission_type = line_agent.commission_id.commission_type
            if commission_type == 'fixed' and line_agent.commission_id.fix_qty:
                subtotal = line_agent.invoice_line_id.price_subtotal
                fix_qty = line_agent.commission_id.fix_qty
                vals = {'quantity': subtotal * (fix_qty / 100.0)}
                self.write(cr, uid, line_agent.id, vals, context=context)

    @api.onchange("agent_id")
    def do_set_commission_and_recalulate(self):
        """Change commission and recalculate commissions
        """
        agent = self.agent_id
        if agent:
            self.commission_id = agent.commission
            subtotal = self.invoice_line_id.price_subtotal
            self.quantity = subtotal * (agent.commission.fix_qty / 100.0)

    @api.onchange("commission_id")
    def do_check_commission_and_recalculate(self):
        """Recalculate commissions, check selected commission
        and raise a warning when selected commission
        is not the default provided for sale agent
        and default partner commission have sections
        """
        commission = self.commission_id
        if commission:
            agent_commission = self.agent_id.commission
            subtotal = self.invoice_line_id.price_subtotal
            self.quantity = subtotal * (agent_commission.fix_qty / 100.0)

            if self.agent_id and commission.sections:
                if commission != agent_commission:
                    return {
                        "warning": {
                            "title": _('Fee installments!'),
                            "message": _(
                                "Selected commission has been assigned "
                                "by sections and it does not match "
                                "the one defined to the selected agent."
                                "These sections shall apply only on this bill."
                            )
                        }
                    }


class account_invoice_line(models.Model):
    """Relation between commissions and invoice"""

    _inherit = "account.invoice.line"

    commission_ids = fields.One2many(
        "invoice.line.agent",
        "invoice_line_id",
        string="Commissions",
        help="Commissions asociated to invoice line."
    )


class account_invoice(models.Model):
    """Inherit the invoice to add the sales representative"""

    _inherit = "account.invoice"

    agent_id = fields.Many2one('sale.agent', 'Agent')
    agent_code = fields.Char(
        string="Agent code",
        related="agent_id.code",
        readonly=True,

    )
    country = fields.Many2one(
        "res.country",
        string="Country",
        related="partner_id.country_id",
        readonly=True
    )

    def onchange_partner_id(self, cr, uid, ids, type, part,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            context=None):
        """When change partner we find the agent associated
        """
        res = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids,
            type, part, date_invoice,
            payment_term, partner_bank_id, company_id
        )
        if part and res.get('value', False):
            partner_obj = self.pool['res.partner']
            partner = partner_obj.browse(cr, uid, part, context=context)
            if partner.commission_ids:
                agent_id = partner.commission_ids[0].agent_id.id
                res['value']['agent_id'] = agent_id
        return res

    def _refund_cleanup_lines(self, cr, uid, lines, context=None):
        """ugly function to map all fields of account.invoice.line
        when creates refund invoice"""
        res = super(account_invoice, self)._refund_cleanup_lines(
            cr, uid, lines, context=context
        )
        for line in res:
            if 'commission_ids' in line[2]:
                commission_ids = [(6, 0, line[2].get('commission_ids', []))]
                line[2]['commission_ids'] = commission_ids
        return res
