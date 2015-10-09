# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    'name': 'Sale stock commissions',
    'version': '8.0.1.0.0',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza',
    "category": "Generic Modules/Sales & Purchases",
    'license': 'AGPL-3',
    'depends': [
        'sale_commission',
        'sale_stock'
    ],
    'contributors': [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
    ],
    "data": [],
    "installable": True,
    "auto_install": True,
}
