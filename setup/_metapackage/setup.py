import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-commission",
    description="Meta package for oca-commission Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-sale_commission',
        'odoo14-addon-sale_commission_formula',
        'odoo14-addon-sale_commission_geo_assign',
        'odoo14-addon-sale_commission_pricelist',
        'odoo14-addon-sale_commission_salesman',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
