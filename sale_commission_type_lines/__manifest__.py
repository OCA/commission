{
    "name": "Sale Commission Type Lines",
    "version": "14.0.1.0.1",
    "author": "Ilyas," "Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["sale_commission"],
    "website": "https://github.com/OCA/commission",
    "maintainers": ["ilyasProgrammer"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/sale_commission_view.xml",
        "views/sale_order_view.xml",
        "views/commission_item.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "installable": True,
}
