# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    area_manager_id = fields.Many2one(
        comodel_name="res.partner",
        domain="[('agent', '=', True), ('area_manager', '=', True)]")
    area_manager = fields.Boolean(
    	string="Area Manager")
    area_manager_sub_agent_ids = fields.One2many(
    	comodel_name="res.partner", inverse_name="area_manager_id",
    	string="Agents")
    commission_for_areamanager = fields.Many2one(
        string="Commission For AreaManager", comodel_name="sale.commission")
