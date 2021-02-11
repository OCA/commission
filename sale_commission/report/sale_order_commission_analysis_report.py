from odoo import tools
from odoo import models, fields, api
from psycopg2.extensions import AsIs


class SaleOrderCommissionAnalysisReport(models.Model):
    _name = "sale.order.commission.analysis.report"
    _description = "Sale Order Commission Analysis Report"
    _auto = False
    _rec_name = 'commission_id'

    @api.model
    def _get_selection_order_state(self):
        return self.env['sale.order'].fields_get(
            allfields=['state'])['state']['selection']

    order_state = fields.Selection(selection='_get_selection_order_state',
                                   string='Order Status', readonly=True)
    date_order = fields.Date('Order Date', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    salesman_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    agent_id = fields.Many2one('res.partner', 'Agent', readonly=True)
    categ_id = fields.Many2one(
        'product.category',
        'Category of Product',
        readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    quantity = fields.Float('# of Qty', readonly=True)
    price_unit = fields.Float('Price unit', readonly=True)
    price_subtotal = fields.Float('Price subtotal', readonly=True)
    percentage = fields.Integer('Percentage of commission', readonly=True)
    amount = fields.Float('Amount', readonly=True)
    order_line_id = fields.Many2one(
        'sale.order.line',
        'Order line',
        readonly=True)
    commission_id = fields.Many2one(
        'sale.commission',
        'Sale commission',
        readonly=True)

    def _select(self):
        select_str = """
            SELECT MIN(sola.id) AS id,
            so.partner_id AS partner_id,
            so.state AS order_state,
            so.date_order AS date_order,
            sol.company_id AS company_id,
            sol.salesman_id AS salesman_id,
            rp.id AS agent_id,
            pt.categ_id AS categ_id,
            sol.product_id AS product_id,
            pt.uom_id AS uom_id,
            SUM(sol.product_uom_qty) AS quantity,
            AVG(sol.price_unit) AS price_unit,
            SUM(sol.price_subtotal) AS price_subtotal,
            AVG(sc.fix_qty) AS percentage,
            SUM(sola.amount) AS amount,
            sol.id AS order_line_id,
            sola.commission AS commission_id
        """
        return select_str

    def _from(self):
        from_str = """
            sale_order_line_agent sola
            LEFT JOIN sale_order_line sol ON sol.id = sola.object_id
            INNER JOIN sale_order so ON so.id = sol.order_id
            LEFT JOIN sale_commission sc ON sc.id = sola.commission
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN res_partner rp ON sola.agent = rp.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY so.partner_id,
            so.state,
            so.date_order,
            sol.company_id,
            sol.salesman_id,
            rp.id,
            pt.categ_id,
            sol.product_id,
            pt.uom_id,
            sol.id,
            sola.commission
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
