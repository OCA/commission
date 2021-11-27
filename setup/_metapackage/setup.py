import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-commission",
    description="Meta package for oca-commission Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-hr_commission',
        'odoo13-addon-sale_commission',
        'odoo13-addon-sale_commission_delegated_partner',
        'odoo13-addon-sale_commission_formula',
        'odoo13-addon-sale_commission_pricelist',
        'odoo13-addon-sale_commission_salesman',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
