# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    area_manager_id = fields.Many2one(
        comodel_name="res.partner", string="Area Manager",
        domain="[('agent', '=', True), ('area_manager', '=', True)]",
        help="Area manager for the current agent")
    area_manager = fields.Boolean(
        string="Is Area Manager", help="This agent is an area manager")
    area_manager_sub_agent_ids = fields.One2many(
        comodel_name="res.partner", inverse_name="area_manager_id",
        string="Agents", readonly=True)
    commission_for_areamanager = fields.Many2one(
        string="Commission For Area Manager", comodel_name="sale.commission",
        help="Commission for area manager applied to the current agent")
