# Copyright (C) 2020, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sales Commissions Teams',
    'version': '12.0.1.2.0',
    'author': 'Open Source Integrators,'
              'Odoo Community Association (OCA)',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'depends': [
        'sale_management',
        'sale_commission'
    ],
    'website': 'https://github.com/OCA/commission',
    'development_status': 'Mature',
    'maintainers': [
        'osi-scampbell',
    ],
    'data': [
        'views/res_config_settings.xml'
    ],
    'installable': True,
}
