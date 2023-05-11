# © 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Commission Type Lines Discount",
    "summary": "Advanced commissions rules with discount",
    "version": "14.0.1.0.1",
    "author": "Ilyas," "Ooops404," "Odoo Community Association (OCA)",
    "contributors": ["Ilyas"],
    "maintainers": ["ilyasProgrammer"],
    "website": "https://github.com/OCA/commission",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["sale_commission_product_criteria"],
    "data": [
        "views/views.xml",
        "views/res_config_settings_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "post_init_hook": "enable_discounts",
}
