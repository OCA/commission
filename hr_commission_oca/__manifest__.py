# Copyright 2015-2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Jo??o Marques
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "HR commissions",
    "version": "15.0.1.0.0",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/commission",
    "category": "Commissions",
    "depends": ["sale_commission", "hr"],
    "license": "AGPL-3",
    "data": [
        "views/res_partner_view.xml",
        "views/sale_commission_settlement_views.xml",
    ],
    "installable": True,
}
