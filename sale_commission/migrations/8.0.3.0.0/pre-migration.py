# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute("""ALTER TABLE sale_commission_settlement
                  ADD COLUMN company_id int""")
    cr.execute("""ALTER TABLE sale_commission ADD COLUMN company_id int""")
    cr.execute("""
        UPDATE sale_commission_settlement scs
        SET company_id = res_partner.company_id
        FROM res_partner
        WHERE res_partner.id = scs.agent""")
