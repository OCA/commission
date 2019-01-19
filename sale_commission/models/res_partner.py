# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agents = fields.Many2many(
        comodel_name="res.partner", relation="partner_agent_rel",
        column1="partner_id", column2="agent_id",
        domain=[('agent', '=', True)])
    # Fields for the partner when it acts as an agent
    agent = fields.Boolean(
        string="Creditor/Agent",
        help="Check this field if the partner is a creditor or an agent.")
    agent_type = fields.Selection(
        selection=[("agent", "External agent")], string="Type", required=True,
        default="agent")
    commission = fields.Many2one(
        string="Commission", comodel_name="sale.commission",
        help="This is the default commission used in the sales where this "
             "agent is assigned. It can be changed on each operation if "
             "needed.")
    settlement = fields.Selection(
        selection=[("monthly", "Monthly"),
                   ("quaterly", "Quarterly"),
                   ("semi", "Semi-annual"),
                   ("annual", "Annual")],
        string="Settlement period", default="monthly", required=True)
    settlements = fields.One2many(
        comodel_name="sale.commission.settlement", inverse_name="agent",
        readonly=True)

    @api.onchange('agent_type')
    def onchange_agent_type(self):
        if self.agent_type == 'agent' and self.agent:
            self.supplier = True

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        """Change agents if the parent company changes."""
        res = super(ResPartner, self).onchange_parent_id()
        if not self.is_company:
            self.agents = self.parent_id.agents
        return res

    @api.model
    def create(self, vals):
        """Propagate agents from parent to child"""
        if (vals.get('parent_id') and not vals.get('agents') and
                not vals.get('is_company')):
            vals['agents'] = [
                (4, x) for x in self.browse(vals['parent_id']).agents.ids
            ]
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        """Propagate agents change in the parent partner to the child
        contacts.
        """
        if vals.get('agents'):
            for record in self:
                childs = record.mapped('child_ids').filtered(lambda r: (
                    (not r.agents or r.agents == record.agents) and
                    not r.is_company
                ))
                if childs:
                    childs.write({'agents': vals['agents']})
        return super(ResPartner, self).write(vals)

    @api.model
    def default_get(self, fields_list):
        defaults = super(ResPartner, self).default_get(fields_list)
        if 'parent_id' in defaults:
            defaults['agents'] = [
                (4, x) for x in self.browse(defaults['parent_id']).agents.ids
            ]
        return defaults
