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
        insert into res_partner_agent (partner_id, agent_id, commission_id)
        (select par.partner_id, par.agent_id, rp.commission
        from partner_agent_rel par
        inner join res_partner rp on rp.id=par.agent_id
        where rp.commission is not null)""")
