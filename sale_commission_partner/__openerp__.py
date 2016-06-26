# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) bisneSmart
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
    'name': 'Sale commission partner',
    'version': '8.0.1.0.0',
    'author': 'bisneSmart',
    "category": "Generic Modules/Sales & Purchases",
    'license': 'AGPL-3',
    'depends': [
        'sale_commission',
    ],
    'contributors': [
        "Rubén Cabrera <rcabrera@bisnesmart.com>",
    ],
    "data": [
        "views/settlement_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
