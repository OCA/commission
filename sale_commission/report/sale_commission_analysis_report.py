# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, tools


class SaleCommissionAnalysisReport(models.Model):
    _name = "sale.commission.analysis.report"
    _description = "Sale Commission Analysis Report"
    _auto = False
    _rec_name = 'commission_id'

    invoice_state = fields.Selection([
        ('cancel', 'Cancelled'),
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('proforma', 'Proforma'),
        ('proforma2', 'Proforma2')], 'Invoice Status', readonly=True)
    date_invoice = fields.Date('Date Invoice', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    agent_id = fields.Many2one('res.partner', 'Agent', readonly=True)
    categ_id = fields.Many2one('product.category',
            'Category of Product', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
    quantity = fields.Float('# of Qty', readonly=True)
    price_unit = fields.Float('Price unit', readonly=True)
    price_subtotal = fields.Float('Price subtotal', readonly=True)
    percentage = fields.Integer('Percentage of commission', readonly=True)
    amount = fields.Float('Amount', readonly=True)
    invoice_line_id = fields.Many2one('account.invoice.line',
            'Invoice line', readonly=True)
    settled = fields.Boolean('Settled', readonly=True)
    commission_id = fields.Many2one('sale.commission',
            'Sale commission', readonly=True)

    def _select(self):
        select_str = """
            SELECT min(aila.id) as id, ai.partner_id partner_id,
            ai.state invoice_state,
            ai.date_invoice,
            ail.company_id company_id,
            rp.id agent_id,
            pt.categ_id categ_id,
            ail.product_id product_id,
            pt.uom_id,
            ail.quantity,
            ail.price_unit,
            ail.price_subtotal,
            sc.fix_qty percentage,
            aila.amount,
            ail.id invoice_line_id,
            aila.settled,
            aila.commission commission_id
        """
        return select_str

    def _from(self):
        from_str = """
            account_invoice_line_agent aila
            LEFT JOIN account_invoice_line ail ON ail.id = aila.invoice_line
            LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN sale_commission sc ON sc.id = aila.commission
            LEFT JOIN product_product pp ON pp.id = ail.product_id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN res_partner rp ON aila.agent = rp.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY ai.partner_id,
            ai.state,
            ai.date_invoice,
            ail.company_id,
            rp.id,
            pt.categ_id,
            ail.product_id,
            pt.uom_id,
            ail.quantity,
            sc.fix_qty,
            aila.amount,
            ail.id,
            aila.settled,
            aila.commission
        """
        return group_by_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, "sale_commission_analysis_report")
        cr.execute("""CREATE or REPLACE VIEW sale_commission_analysis_report as (
            %s
            FROM ( %s )
            %s
            )""" % (self._select(), self._from(), self._group_by()))
