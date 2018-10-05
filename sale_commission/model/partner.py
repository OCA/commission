# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields


class res_partner(models.Model):
    """Add some fields related to commissions"""

    _inherit = "res.partner"

    commission_ids = fields.One2many(
        "res.partner.agent",
        "partner_id",
        string="Agents"
    )

    agent = fields.Boolean(
        string="Creditor/Agent",
        help="If you check this field will be available as creditor or agent."
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
