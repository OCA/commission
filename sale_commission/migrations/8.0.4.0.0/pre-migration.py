# -*- coding: utf-8 -*-
# Copyright (C) 2016 - TODAY Magno Costa - Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute("""ALTER TABLE sale_commission_settlement_line
                  ADD COLUMN effective_date date""")
    cr.execute("""
        UPDATE sale_commission_settlement_line
        SET effective_date = date""")
    cr.execute("""
        UPDATE sale_commission_settlement_line
        SET settled_amount = account_invoice.commission_total
        FROM account_invoice WHERE account_invoice.id =
            sale_commission_settlement_line.invoice""")
