#  -*- coding: utf-8 -*-
#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    """Populate company field for settlements"""
    # Populate company_id for sale.commission.settlement,
    # get the company from the settlement's agent's company
    cr.execute(
        'UPDATE sale_commission_settlement '
        'SET company_id = res_partner.company_id '
        'FROM res_partner '
        'WHERE sale_commission_settlement.agent = res_partner.id')
