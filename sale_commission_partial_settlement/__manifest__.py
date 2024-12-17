# Copyright 2023 Nextev
{
    "name": "Sales commissions based on paid amount",
    "version": "14.0.2.0.0",
    "author": "Nextev Srl," "Ooops," "Odoo Community Association (OCA)",
    "maintainers": ["aleuffre", "renda-dev", "PicchiSeba"],
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["sale_commission"],
    "website": "https://github.com/OCA/commission",
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_line_agent_views.xml",
        "views/account_invoice_line_agent_partial_views.xml",
        "views/res_config_settings_view.xml",
        "views/sale_commission_settlement_line_partial_views.xml",
        "views/sale_commission_settlement_view.xml",
        "views/sale_commission_view.xml",
    ],
    "installable": True,
}
