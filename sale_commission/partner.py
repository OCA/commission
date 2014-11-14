# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
#    $Id$
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

"""añadimos algún campo relacionado con el intrastat"""

from osv import fields, orm


class res_partner(orm.Model):

    """añadimos algún campo relacionado con elas comisiones"""

    _name = "res.partner"
    _inherit = "res.partner"
    _columns = {
        'commission_ids': fields.one2many('res.partner.agent', 'partner_id', 'Agents'),
        'agent': fields.boolean('Creditor/Agent',
                                help="If you check this field will be available as creditor or agent.")
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
