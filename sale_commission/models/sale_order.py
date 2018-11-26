# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
        string="Commissions",
        compute="_compute_commission_total",
        store=True,
    )

    def recompute_lines_agents(self):
        self.mapped('order_line').recompute_agents()


class SaleOrderLine(models.Model):
    _inherit = [
        "sale.order.line",
        "sale.commission.mixin",
    ]
    _name = "sale.order.line"

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name="sale.order.line.agent",
    )

    @api.model
    def create(self, vals):
        """Add agents for records created from automations instead of UI."""
        if 'agents' not in vals:
            order = self.env['sale.order'].browse(vals['order_id'])
            vals['agents'] = self._prepare_agents_vals_partner(
                order.partner_id,
            )
        return super().create(vals)

    def _prepare_agents_vals(self):
        self.ensure_one()
        res = super()._prepare_agents_vals()
        return res + self._prepare_agents_vals_partner(
            self.order_id.partner_id,
        )

    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        vals['agents'] = [
            (0, 0, {'agent': x.agent.id,
                    'commission': x.commission.id}) for x in self.agents]
        return vals


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.commission.line.mixin"
    _name = "sale.order.line.agent"

    object_id = fields.Many2one(
        comodel_name="sale.order.line",
        oldname="sale_line",
    )
    # Overwritten fields for indicating the source for computing comm. amount
    source_product_id = fields.Many2one(
        related="object_id.product_id",
        readonly=True,
    )
    source_quantity = fields.Float(
        related="object_id.product_uom_qty",
        readonly=True,
    )
    source_total = fields.Monetary(
        related="object_id.price_subtotal",
        readonly=True,
    )
    currency_id = fields.Many2one(
        related="object_id.currency_id",
        readonly=True,
    )
