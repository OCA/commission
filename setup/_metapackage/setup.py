import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-commission",
    description="Meta package for oca-commission Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-sale_commission',
        'odoo10-addon-sale_commission_areamanager',
        'odoo10-addon-sale_commission_formula',
        'odoo10-addon-sale_commission_pricelist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
