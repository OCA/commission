# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Abstract (http://www.abstract.it)
#    @author Davide Corio <davide.corio@abstract.it>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models


class Commission(models.Model):
    _inherit = 'commission'

    def __init__(self, name):
        super(Commission, self).__init__(name)
        formula = ('formula', 'Formula')
        commission_type = self._columns['commission_type'].selection
        if formula not in commission_type:
            commission_type.append(formula)
