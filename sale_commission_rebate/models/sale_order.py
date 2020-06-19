# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rebate_price = fields.Float(
        string="Rebate Price",
        compute="_compute_supplierinfo_id",
        store=True,
        digits=dp.get_precision('Product Price'),
    )
    supplierinfo_id = fields.Many2one(
        'product.supplierinfo',
        string="Rebate Issuer",
        compute="_compute_supplierinfo_id",
        store=True)

    @api.multi
    @api.depends('product_id')
    def _compute_supplierinfo_id(self):
        for rec in self:
            if not rec.product_id:
                return
            supplierinfos = rec._get_supplierinfos()
            if supplierinfos:
                rec.supplierinfo_id = supplierinfos[0]
                rec.rebate_price = supplierinfos[0].rebate_price
                rec.agents = [
                    (0, 0, vals) for vals in rec._prepare_agents_vals()
                ]

    @api.multi
    def _get_supplierinfos(self):
        self.ensure_one()
        supplierinfos = self.env['product.supplierinfo'].search(
            [
                '&',
                '&',
                ('is_agent',
                    '=',
                    True),
                '&',
                ('date_start',
                    '<=',
                    self.order_id.date_order),
                ('date_end',
                    '>=',
                    self.order_id.date_order),
                '|',
                ('product_id',
                    '=',
                    self.product_id.id),
                ('product_tmpl_id',
                    '=',
                    self.product_id.product_tmpl_id.id),
            ])
        if supplierinfos:
            return supplierinfos
        return False

    @api.depends('supplierinfo_id')
    def get_rebate_price(self):
        if self.supplierinfo_id:
            self.rebate_price = self.supplierinfo_id.rebate_price

    @api.model
    def _prepare_agents_vals(self):
        """Agents taken from the products (rebates)
           TODO: Allow to change agent in case there are more than one
        """
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_agents_vals()
        agent = self.supplierinfo_id
        if agent:
            res.append({
                'agent': agent[0].name.id,
                'commission': agent[0].name.commission.id
            })
        return res
