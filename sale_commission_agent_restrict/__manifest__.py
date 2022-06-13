{
    "name": "Sales Commissions Agent Restrict",
    "version": "14.0.1.0.1",
    "author": "Ooops404, Ilyas, Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "https://github.com/OCA/commission",
    "license": "AGPL-3",
    "depends": ["sale_commission"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/sale_order_view.xml",
    ],
    "uninstall_hook": "restore_access_rules",
    "installable": True,
}
