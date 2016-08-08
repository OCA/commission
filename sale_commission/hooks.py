# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def set_commission_total(cr):
    """
    When there are to many sale.order created it takes a very long time to
    create the computed field commission_total, in order to ease the
    installation we create the field manually.
    As its value will be computed from data that still doesn't exist, its value
    will be always 0, so there's no need to be filled.
    :param cr: database cursor
    :return: void
    """
    cr.execute("""
        ALTER TABLE sale_order
        ADD COLUMN commission_total double precision;""")
