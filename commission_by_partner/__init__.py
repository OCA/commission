# -*- coding: utf-8 -*-
# © 2015 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# © 2015 Javier Colmenero Fernández (<javier@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from . import models


def post_init_hook(cr, registry):
    cr.execute("SELECT id FROM res_partner_agent")
    if not cr.fetchall():
        copy_agents_into_commission_ids(cr)


def copy_agents_into_commission_ids(cr):
    cr.execute("""
        INSERT INTO res_partner_agent
        (partner_id, agent_id, commission_id, company_id)
        (select par.partner_id, agent_id, rp.commission, rp2.company_id
        FROM partner_agent_rel par
        INNER JOIN res_partner rp ON rp.id=par.agent_id
        INNER JOIN res_partner rp2 ON rp2.id=par.partner_id
        WHERE rp.commission is not null);""")
