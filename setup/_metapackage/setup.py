import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-commission",
    description="Meta package for oca-commission Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-contract_commission',
        'odoo12-addon-hr_commission',
        'odoo12-addon-sale_commission',
        'odoo12-addon-sale_commission_delegated_partner',
        'odoo12-addon-sale_commission_formula',
        'odoo12-addon-sale_commission_pricelist',
        'odoo12-addon-sale_commission_salesman',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
