# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class SaleAgentPlan(models.Model):

    _name = 'sale.agent.plan'

    name = fields.Char(required=True)
    lines = fields.One2many('sale.agent.plan.line', 'plan', copy=True)

    @api.multi
    def get_product_commission(self, product=False):
        commission_line = self.lines.filtered(
            lambda r: r.product.id == product)
        if not commission_line:
            commission_line = self.lines.filtered(
                lambda r: r.product.id is False)
        return commission_line.commission

    @api.multi
    def unlink(self):
        for plan in self:
            partner_ids = self.env["res.partner"].\
                search([('plan', '=', plan.id)])
            if partner_ids:
                raise exceptions.Warning(_("Cannot delete this plan, because "
                                           "it is related to partners"))
        return super(SaleAgentPlan, self).unlink()


class SaleAgentPlanLine(models.Model):

    _name = 'sale.agent.plan.line'

    product = fields.Many2one('product.product')
    commission = fields.Many2one('sale.commission', required=True)
    plan = fields.Many2one('sale.agent.plan')
