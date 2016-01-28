# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agents = fields.Many2many(
        comodel_name="res.partner", relation="partner_agent_rel",
        column1="partner_id", column2="agent_id",
        domain="[('agent', '=', True)]")
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
