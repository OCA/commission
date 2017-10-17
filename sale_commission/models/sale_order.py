# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.agents.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.order_line:
                record.commission_total += sum(x.amount for x in line.agents)

    commission_total = fields.Float(
        string="Commissions", compute="_compute_commission_total",
        store=True)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.ensure_one()
        res = super(SaleOrder, self).onchange_partner_id()
        # workaround for https://github.com/odoo/odoo/issues/17618
        for order_line in self.order_line:
            order_line.agents = None
        return res

    @api.onchange('fiscal_position_id')
    def _compute_tax_id(self):
        self.ensure_one()
        res = super(SaleOrder, self)._compute_tax_id()
        # workaround for https://github.com/odoo/odoo/issues/17618
        for order_line in self.order_line:
            order_line.agents = None
        return res

    @api.model
    def _prepare_line_agents_data(self, line):
        rec = []
        for agent in self.partner_id.agents:
            rec.append({
                'agent': agent.id,
                'commission': agent.commission.id,
            })
        return rec

    @api.multi
    def recompute_lines_agents(self):
        for order in self:
            for line in order.order_line:
                line.agents.unlink()
                line_agents_data = order._prepare_line_agents_data(line)
                line.agents = [(
                    0,
                    0,
                    line_agent_data) for line_agent_data in line_agents_data]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_agents(self):
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for agent in partner.agents:
                agents.append({'agent': agent.id,
                               'commission': agent.commission.id})
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name="sale.order.line.agent", inverse_name="sale_line",
        copy=True, readonly=True, default=_default_agents)
    commission_free = fields.Boolean(
        string="Comm. free", related="product_id.commission_free",
        store=True, readonly=True)

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        vals['agents'] = [
            (0, 0, {'agent': x.agent.id,
                    'commission': x.commission.id}) for x in self.agents]
        return vals


class SaleOrderLineAgent(models.Model):
    _name = "sale.order.line.agent"
    _rec_name = "agent"

    sale_line = fields.Many2one(
        comodel_name="sale.order.line", required=True, ondelete="cascade")
    agent = fields.Many2one(
        comodel_name="res.partner", required=True, ondelete="restrict",
        domain="[('agent', '=', True)]")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")
    amount = fields.Float(compute="_compute_amount", store=True)

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(sale_line, agent)',
         'You can only add one time each agent.')
    ]

    @api.onchange('agent')
    def onchange_agent(self):
        self.commission = self.agent.commission

    @api.depends('sale_line.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            if (not line.sale_line.product_id.commission_free and
                    line.commission):
                if line.commission.amount_base_type == 'net_amount':
                    subtotal = (line.sale_line.price_subtotal -
                                (line.sale_line.product_id.standard_price *
                                 line.sale_line.product_uom_qty))
                else:
                    subtotal = line.sale_line.price_subtotal
                if line.commission.commission_type == 'fixed':
                    line.amount = subtotal * (line.commission.fix_qty / 100.0)
                else:
                    line.amount = line.commission.calculate_section(subtotal)
