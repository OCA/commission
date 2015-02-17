
# -*- encoding: utf-8 -*-
##############################################################################
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
    'name': 'HR commission',
    'version': '1.0',
    'author': 'Pexego',
    "category": "Generic Modules/Sales & Purchases",
    'depends': ['sale_commission', 'hr'],
    'contributors': [
        "Davide Corio <davide.corio@domsense.com>",
        "Joao Alfredo Gama Batista <joao.gama@savoirfairelinux.com>",
        "Sandy Carter <sandy.carter@savoirfairelinux.com>",
        "Giorgio Borelli <giorgio.borelli@abstract.it>",
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>"],
    "data": ["views/sale_agent_view.xml"],
    "active": True,
    "installable": True,
    "auto_install": True,
}
