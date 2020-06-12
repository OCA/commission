# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleCommissionMixin(models.AbstractModel):
    _name = 'sale.commission.mixin'
    _description = "Mixin model for applying to any object that wants to " \
                   "handle commissions"

    @api.model
    def _prepare_agents_vals_partner(self, partner):
        """Utility method for getting agents of a partner."""
        rec = []
        for agent in partner.agents:
            rec.append((0, 0, {
                'agent': agent.id,
                'commission': agent.commission.id,
            }))
        return rec

    @api.model
    def _default_agents(self):
        agents = []
        context = self.env.context
        if context.get('partner_id'):
            partner = self.env['res.partner'].browse(context['partner_id'])
            agents = self._prepare_agents_vals_partner(partner)
        return agents

    agents = fields.One2many(
        comodel_name="sale.commission.line.mixin",
        inverse_name="object_id",
        string="Agents & commissions",
        help="Agents/Commissions related to the invoice line.",
        default=lambda self: self._default_agents(),
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

    @api.depends('commission_free', 'agents')
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

    def _prepare_agents_vals(self, vals=None):
        """Hook method for preparing the values of agents.

        :param: self: Record of the object that is being handled.
        """
        assert self or vals
        return []

    def recompute_agents(self):
        """Force a recomputation of the agents according prepare method."""
        for record in self:
            record.agents = (
                [(3, x.id) for x in record.agents] +
                record._prepare_agents_vals()
            )

    def button_edit_agents(self):
        self.ensure_one()
        view = self.env.ref(
            'sale_commission.view_sale_commission_mixin_agent_only'
        )
        return {
            'name': _('Agents'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }


class SaleCommissionLineMixin(models.AbstractModel):
    _name = "sale.commission.line.mixin"
    _description = "Mixin model for having commission agent lines in " \
                   "any object inheriting from this one"
    _rec_name = "agent"

    _sql_constraints = [
        ('unique_agent', 'UNIQUE(object_id, agent)',
         'You can only add one time each agent.')
    ]

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
    amount = fields.Monetary(
        string="Commission Amount",
        compute="_compute_amount",
        store=True,
    )
    # Fields to be overriden with proper source (via related or computed field)
    currency_id = fields.Many2one(comodel_name='res.currency')

    def _compute_amount(self):
        """Compute method to be implemented by inherited models."""
        raise NotImplementedError()

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        """Get the commission amount for the data given. To be called by
        compute methods of children models.
        """
        self.ensure_one()
        if product.commission_free or not commission:
            return 0.0
        if commission.amount_base_type == 'net_amount':
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([
                0, subtotal - product.standard_price * quantity,
            ])
        if commission.commission_type == 'fixed':
            return subtotal * (commission.fix_qty / 100.0)
        elif commission.commission_type == 'section':
            return commission.calculate_section(subtotal)

    @api.onchange('agent')
    def onchange_agent(self):
        self.commission = self.agent.commission
