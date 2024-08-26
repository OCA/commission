# Copyright 2015 Quartile Alejandro Sánchez Ramírez (<http://www.asr-oss.com>)
# Copyright 2024 Nextev Srl <odoo@nextev.it>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale commissions product",
    "version": "16.0.1.0.0",
    "author": "Asr Oss - Alejandro Sánchez, Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale_commission",
        "account_commission",
    ],
    "website": "https://github.com/OCA/commission",
    "data": [
        "views/product_view.xml",
    ],
    "installable": True,
}
