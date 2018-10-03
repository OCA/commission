import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-commission",
    description="Meta package for oca-commission Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-hr_commission',
        'odoo11-addon-sale_commission',
        'odoo11-addon-sale_commission_formula',
        'odoo11-addon-sale_commission_pricelist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
