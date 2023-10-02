import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-commission",
    description="Meta package for oca-commission Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_commission>=16.0dev,<16.1dev',
        'odoo-addon-commission>=16.0dev,<16.1dev',
        'odoo-addon-hr_commission>=16.0dev,<16.1dev',
        'odoo-addon-sale_commission>=16.0dev,<16.1dev',
        'odoo-addon-sale_commission_salesman>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
