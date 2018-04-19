import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-commission",
    description="Meta package for oca-commission Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-contract_commission',
        'odoo8-addon-hr_commission',
        'odoo8-addon-sale_commission',
        'odoo8-addon-sale_commission_formula',
        'odoo8-addon-sale_commission_product',
        'odoo8-addon-sale_stock_commission',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
