# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    plan = fields.Many2one('sale.agent.plan')
