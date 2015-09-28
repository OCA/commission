# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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


def restore_relation_data(cr):
    cr.execute(
        """
        INSERT INTO agent_commission_rel (partner_id, commission_id)
        SELECT agent_id, commission_id FROM tmp_mig_agent_commissions
        """)
    cr.execute("""DROP TABLE tmp_mig_agent_commissions""")
    cr.execute(
        """
        INSERT INTO settlement_commission_line_rel
        (commission_line_id, settlement_id)
        SELECT agent_line_id, settlmeent_id
        FROM tmp_mig_settlement_line_rel
        """)
    cr.execute("""DROP TABLE tmp_mig_settlement_line_rel""")


def migrate(cr, installed_version):
    restore_relation_data(cr)
