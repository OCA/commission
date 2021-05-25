# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    zone_agent_ids = fields.Many2many(
        comodel_name='partner.zone',
        relation='agent_zone_rel',
        column1='agent_id',
        column2='zone_id',
        string='Agent Zones',
    )

    def _compute_zone_agents(self):
        self.agents |= self.zone_ids.mapped('agent_ids')

    @api.onchange('zone_ids')
    def _onchange_commission_zone(self):
        if self.zone_ids:
            self._compute_zone_agents()

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.zone_ids and not res.agents:
            res._compute_zone_agents()
        return res

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if self.zone_ids and not vals.get('agents') and not self.agents:
            self._compute_zone_agents()
        return res
