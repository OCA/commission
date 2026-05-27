==========================================
Sale Commission Product Criteria Sections
==========================================

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge2| image:: https://img.shields.io/badge/github-rodmad85-lightgray.png?logo=github
    :target: https://github.com/rodmad85/commission/tree/16.0/commission_product_criteria_sections
    :alt: rodmad85/commission

|badge1| |badge2|

This module extends sale_commission_product_criteria to allow configuring
section-based (tiered) commission rates per product criteria rule.

Each commission item can define its own set of rate sections with amount
ranges and percentages, enabling complex commission structures where
different products have different tiered rates based on the order amount.

**Table of contents**

.. contents::
   :local:

Configuration
=============

Go to Commissions > Configuration > Commission Types

In a record of type "Product criteria", create or edit a commission item
and set "Compute Price" to "By sections".

Define the rate tiers by adding lines with:

* **From** - lower bound of the amount range
* **To** - upper bound of the amount range
* **Percent** - commission percentage for this range

Usage
=====

When a sale order is confirmed, the commission for each line is calculated
by finding the matching commission item rule for the product. If the rule
uses "By sections", the commission amount is computed by selecting the
rate tier that matches the line subtotal and applying the corresponding
percentage.

For example, a rule with sections:

* 0 - 100: 5%
* 100 - 500: 8%
* 500+: 10%

A sale of 200 would grant 200 * 8% = 16 in commission.
A sale of 600 would grant 600 * 10% = 60 in commission.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/rodmad85/commission/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* Madooit

Contributors
~~~~~~~~~~~~

* `Madooit <https://github.com/rodmad85>`__:

  * Rodrigo A. Madureira <rodrigomadu85@gmail.com>

Maintainers
~~~~~~~~~~~

This module is maintained by Madooit.

.. image:: https://raw.githubusercontent.com/rodmad85/commission/16.0/logo.png
   :alt: Madooit
   :target: https://github.com/rodmad85

This module is part of the `rodmad85/commission <https://github.com/rodmad85/commission/tree/16.0/commission_product_criteria_sections>`_ project on GitHub.

You are welcome to contribute.
