This module allows to set in the same Commission Type different commission rates according to the product on SO/invoice line.

This is made possible since this module adds a new "Product criteria" type to Commission Type and applies commission rates with the same logic of sale pricelist items.

For example, such a Commission Type can grant:

10% on a specific Product A,
10$ on Product B,
4% on products in Category 1 and
5$ on all other products.

In SO/invoice, system will apply different commissions based on variant/product/category or global, applied hierarchically. This means that for the example above, if product A is assigned to Category 1, commission assigned is 10%, as per variant/product/category/global rule application order.

Furthermore, these commission type items can be accessed and created by a specific menu, to facilitate their management in environments with lots of records.

The form for commission type item can be extended by future modules with further conditions to decide when to apply a specific item.
