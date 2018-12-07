# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleCommissionMixin(models.AbstractModel):
    _name = 'sale.commission.mixin'
    _description = "Mixin model for applying to any object that wants to " \
                   "handle commissions"

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
        comodel_name="sale.commission.line.mixin",
        inverse_name="object_id",
        string="Agents & commissions",
        help="Agents/Commissions related to the invoice line.",
        default=_default_agents,
        copy=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    commission_free = fields.Boolean(
        string="Comm. free",
        related="product_id.commission_free",
        store=True,
        readonly=True,
    )
    commission_status = fields.Char(
        compute="_compute_commission_status",
        string="Commission",
    )

    def _compute_commission_status(self):
        for line in self:
            if line.commission_free:
                line.commission_status = _("Comm. free")
            elif len(line.agents) == 0:
                line.commission_status = _("No commission agents")
            elif len(line.agents) == 1:
                line.commission_status = _("1 commission agent")
            else:
                line.commission_status = _(
                    "%s commission agents"
                ) % len(line.agents)

    @api.model
    def _filter_agent_vals(self, vals):
        """Remove offending commands brought by web client."""
        new_commands = []
        for i, command in enumerate(vals['agents']):
            if i == 0 and command[0] == 5 and len(vals['agents']) > 1:
                # Remove initial [5] command for avoiding integrity error
                continue
            if command[0] == 0 and not command[2]:
                # Remove empty add records
                continue
            new_commands.append(command)
        return new_commands

    @api.model
    def create(self, vals):
        """Workaround for https://github.com/odoo/odoo/issues/17618."""
        if 'agents' in vals:
            vals['agents'] = self._filter_agent_vals(vals)
        return super(SaleCommissionMixin, self).create(vals)

    def write(self, vals):
        """Workaround for https://github.com/odoo/odoo/issues/17618."""
        if 'agents' in vals:
            vals['agents'] = self._filter_agent_vals(vals)
        return super(SaleCommissionMixin, self).write(vals)

    def _prepare_agents_vals(self):
        """Hook method for preparing the values of agents.

        :param: self: Record of the object that is being handled.
        """
        return []

    def recompute_agents(self):
        """Force a recomputation of the agents according prepare method."""
        for record in self:
            record.agents.unlink()
            record.agents = [
                (0, 0, vals) for vals in record._prepare_agents_vals()
            ]


class SaleCommissionLineMixin(models.AbstractModel):
    _name = "sale.commission.line.mixin"
    _description = "Mixin model for having commission agent lines in " \
                   "any object inheriting from this one"

    object_id = fields.Many2one(
        comodel_name="sale.commission.mixin",
        ondelete="cascade",
        required=True,
        copy=False,
        string="Parent",
    )
    agent = fields.Many2one(
        comodel_name="res.partner",
        domain="[('agent', '=', True)]",
        ondelete="restrict",
        required=True,
    )
    commission = fields.Many2one(
        comodel_name="sale.commission",
        ondelete="restrict",
        required=True,
    )

    @api.onchange('agent')
    def onchange_agent(self):
        self.commission = self.agent.commission

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(object_id, agent)',
         'You can only add one time each agent.')
    ]

    @api.multi
    def _get_commission_amount(
            self, commission, subtotal, commission_free, product, quantity):
        self.ensure_one()
        amount = 0.0
        if not commission_free and commission:
            if commission.amount_base_type == 'net_amount':
                # If subtotal (sale_price * quantity) is less than
                # standard_price * quantity, it means that
                # we are selling at lower price than we bought
                # so set amount_base to 0
                amount_base = max(
                    [0,
                     (subtotal - (product.standard_price * quantity))])
            else:
                amount_base = subtotal

            if commission.commission_type == 'fixed':
                amount = amount_base * (commission.fix_qty / 100.0)
            else:
                amount = commission.calculate_section(amount_base)
        return amount
