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

from datetime import date

from openerp.tests import TransactionCase

from ..models.sale_commission import (
    PERIOD_YEAR,
    PERIOD_SEMI,
    PERIOD_QUARTER,
)


class TestPeriodRanges(TransactionCase):
    """
    Test period ranges for settlement wizard
    """

    def setUp(self):
        super(TestPeriodRanges, self).setUp()
        self.w = self.env["sale.commission.make.settle"]

    def test_year(self):
        self.assertEquals(
            self.w._get_period_start(PERIOD_YEAR, date(2015, 6, 1)),
            date(2015, 1, 1), "Yearly period start on Jan 1st")

        self.assertEquals(
            self.w._get_period_end(PERIOD_YEAR, date(2015, 6, 1)),
            date(2015, 12, 31), "Yearly period ends dec 31st")

    def test_semi(self):
        self.assertEquals(
            self.w._get_period_start(PERIOD_SEMI, date(2015, 5, 5)),
            date(2015, 1, 1), "First semester: Jan-June")
        self.assertEquals(
            self.w._get_period_end(PERIOD_SEMI, date(2015, 5, 5)),
            date(2015, 6, 30), "First semester: Jan-June")

        self.assertEquals(
            self.w._get_period_start(PERIOD_SEMI, date(2015, 7, 5)),
            date(2015, 7, 1), "First semester: July-Dec")
        self.assertEquals(
            self.w._get_period_end(PERIOD_SEMI, date(2015, 7, 5)),
            date(2015, 12, 31), "First semester: July-Dec")

    def test_quarter(self):
        for d, s, e, msg in [
            (date(2015, 1, 1), date(2015, 1, 1), date(2015, 3, 31),
             "Q1: Jan-Mar"),
            (date(2015, 6, 30), date(2015, 4, 1), date(2015, 6, 30),
             "Q2: Apr-Jun"),
            (date(2015, 8, 5), date(2015, 7, 1), date(2015, 9, 30),
             "Q3: Jul-Sep"),
            (date(2015, 10, 31), date(2015, 10, 1), date(2015, 12, 31),
             "Q3: Oct-Dec")]:
            self.assertEquals(self.w._get_period_start(PERIOD_QUARTER, d),
                              s, msg)
            self.assertEquals(self.w._get_period_end(PERIOD_QUARTER, d),
                              e, msg)
