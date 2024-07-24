{
    "name": "Sales Commissions Settlement Report",
    "summary": "Settings to customize the settlement report",
    "version": "14.0.1.0.0",
    "author": "Odoo Community Association (OCA), Ooops404, PyTech-SRL",
    "maintainers": ["PicchiSeba"],
    "category": "Sales",
    "website": "https://github.com/OCA/commission",
    "license": "AGPL-3",
    "depends": ["sale_commission"],
    "data": [
        "views/report_settlement_templates.xml",
        "views/res_config_settings_view.xml",
        "views/sale_commission_settlement_view.xml",
    ],
    "installable": True,
}
