# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale commission plan",
    "version": "8.0.1.0.0",
    "category": "Generic Modules/Sales & Purchases",
    "author": "Comunitea, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale_commission_product"
    ],
    "data": [
        "views/product.xml",
        "views/res_partner.xml",
        "views/sale_agent_plan.xml",
        "security/ir.model.access.csv"
    ],
}
