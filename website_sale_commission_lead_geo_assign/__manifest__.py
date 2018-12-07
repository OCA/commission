# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale commission CRM geo assign",
    "summary": "Assign agents to leads according to their location",
    "version": "10.0.1.0.0",
    "development_status": "Beta",
    "category": "Sales management",
    "website": "https://github.com/OCA/commission/tree/"
               "10.0/website_sale_commission_lead_geo_assign",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "website_crm_partner_assign",
        "sale_commission_geo_assign"
    ],
    "data": [
        "data/data.xml",
        "wizards/wizard_geo_assign_lead_view.xml"
    ]
}
