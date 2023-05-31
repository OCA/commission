# Copyright 2023 Nextev Srl
{
    "name": "Sales commission check deposit",
    "version": "14.0.1.0.0",
    "author": "Nextev Srl," "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale_commission",
        "account_check_deposit",
    ],
    "website": "https://github.com/OCA/commission",
    "data": ["views/account_journal_view.xml"],
    "installable": True,
}
