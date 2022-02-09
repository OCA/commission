{
    "name": "Sale Commission by Discount",
    "summary": "Advanced commissions rules",
    "version": "14.0.1.0.1",
    "author": "Ooops," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/commission",
    "contributors": ["Ilyas"],
    "maintainers": ["ilyasProgrammer"],
    "category": "Sales Management",
    "license": "LGPL-3",
    "depends": ["sale_commission"],  # OCA
    "data": [
        "security/ir.model.access.csv",
        "security/groups.xml",
        "views/views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
