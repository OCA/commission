# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 Asr Oss (http://www.asr-oss.com)
#                       Alejandro Sanchez Ramirez <alejandro@asr-oss.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    'name': 'Sale commissions product',
    'version': '1.0',
    'author': 'Asr Oss - Alejandro Sánchez',
    "category": "Generic Modules/Sales & Purchases",
    'license': 'AGPL-3',
    'depends': [
        'sale_commission',
        'sale_stock'
    ],
    'contributors': [
        "Alejandro Sánchez <alejandro@asr-oss.com>",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
