from odoo import tools
from odoo import models, fields, api
from psycopg2.extensions import AsIs


class SaleCommissionAnalysisReport(models.Model):
    _name = "sale.commission.analysis.report"
    _description = "Sale Commission Analysis Report"
    _auto = False
    _rec_name = 'commission_id'

    @api.model
    def _get_selection_invoice_state(self):
        return self.env['account.invoice'].fields_get(
            allfields=['state'])['state']['selection']

    invoice_state = fields.Selection(selection='_get_selection_invoice_state',
                                     string='Invoice Status', readonly=True)
    date_invoice = fields.Date('Date Invoice', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    agent_id = fields.Many2one('res.partner', 'Agent', readonly=True)
    categ_id = fields.Many2one(
        'product.category',
        'Category of Product',
        readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
    quantity = fields.Float('# of Qty', readonly=True)
    price_unit = fields.Float('Price unit', readonly=True)
    price_subtotal = fields.Float('Price subtotal', readonly=True)
    percentage = fields.Integer('Percentage of commission', readonly=True)
    amount = fields.Float('Amount', readonly=True)
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        'Invoice line',
        readonly=True)
    settled = fields.Boolean('Settled', readonly=True)
    commission_id = fields.Many2one(
        'sale.commission',
        'Sale commission',
        readonly=True)

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
            SUM(aila.amount) AS amount,
            ail.id invoice_line_id,
            aila.settled,
            aila.commission commission_id
        """
        return select_str

    def _from(self):
        from_str = """
            account_invoice_line_agent aila
            LEFT JOIN account_invoice_line ail ON ail.id = aila.object_id
            INNER JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN sale_commission sc ON sc.id = aila.commission
            LEFT JOIN product_product pp ON pp.id = ail.product_id
            INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
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
            ail.id,
            aila.settled,
            aila.commission
        """
        return group_by_str

    @api.model
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            "CREATE or REPLACE VIEW %s AS ( %s FROM ( %s ) %s )", (
                AsIs(self._table),
                AsIs(self._select()),
                AsIs(self._from()),
                AsIs(self._group_by())
            ),
        )
