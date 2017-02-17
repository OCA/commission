# -*- coding: utf-8 -*-
# Copyright 2016 Apulia Software srl (<http://www.apuliasoftware.it>)
# Andrea Cometa <a.cometa@apuliasoftware.it>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class PartnerAgentCommission(models.Model):
    """Add specific commission for partner by agent"""
    _name = "partner.agent.commission"

    commission = fields.Many2one(
        string="Commission", comodel_name="sale.commission", required=True,
        help="This is the default commission used in the sales for this "
             "agent for this partner.")
    agent_id = fields.Many2one(
        string="Agent", comodel_name="res.partner", required=True,
        domain="[('agent', '=', True)]")
    partner_id = fields.Many2one(
        string="Partner", comodel_name="res.partner", required=True)


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agents_partner = fields.One2many(
        comodel_name="partner.agent.commission",
        inverse_name="partner_id")

