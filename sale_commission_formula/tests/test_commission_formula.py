# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Abstract (http://www.abstract.it)
#    @author Davide Corio <davide.corio@abstract.it>
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

from openerp.tests.common import TransactionCase


class TestCommissionFormula(TransactionCase):

    def setUp(self):
        super(TestCommissionFormula, self).setUp()
        self.agent = self.env.ref('sale_commission_formula.agent1')
        self.commission = self.env.ref(
            'sale_commission_formula.commission_5perc10extra')
        self.sale_order = self.env.ref('sale_commission_formula.sale_order_1')
        self.sale_order_line = self.env.ref(
            'sale_commission_formula.sale_order_line_1')
        self.agent_commissions = {
            'agent': self.agent.id, 'commission': self.commission.id}

    def test_sale_order_commission(self):
        # we test the '5% + 10% extra' we should return 41.25 since
        # the order total amount is 750.00.
        self.sale_order_line.agents = [(0, 0, self.agent_commissions)]
        self.assertEqual(41.25, self.sale_order.commission_total)

    def test_invoice_commission(self):
        # we confirm the sale order and create the corresponding invoice
        self.sale_order.action_button_confirm()
        invoice_id = self.sale_order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        # we add the commissions on the first invoice line
        invoice_line = invoice.invoice_line[0]
        invoice_line.agents = [(0, 0, self.agent_commissions)]
        # we test the '5% + 10% extra' commissions on the invoice too
        self.assertEqual(41.25, invoice.commission_total)
