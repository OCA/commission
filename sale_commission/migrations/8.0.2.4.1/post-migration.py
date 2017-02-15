# -*- coding: utf-8 -*-
# © 2015 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# © 2015 Javier Colmenero Fernández (<javier@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

__name__ = ('Copy agents to the new One2many commission_ids')


def migrate_agents_field(cr):
    cr.execute("""
        INSERT INTO res_partner_agent
        (partner_id, agent_id, commission_id, default_commission, company_id)
        (select par.partner_id, agent_id, rp.commission, True, null
        FROM partner_agent_rel par
        INNER JOIN res_partner rp ON rp.id=par.agent_id
        WHERE rp.commission is not null);""")


def migrate(cr, version):
    if not version:
        return
    migrate_agents_field(cr)
