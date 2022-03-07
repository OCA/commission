This module adds a new type of "commission type" model allowing user to structure commission type similarly to how pricelist is structured.
This means:

 - commission type lines are now available, where commission rate can be set on global/category/product/variant level. Lines are sorted from variant level to global level, just like in pricelist.
 - commission rate can be either a percentage or a fixed value
 - in SO line, the first applicable commission type line is applied.
 - there is an extra right "Display full agent details on sale order line" in user to enhance agent commission details on SO line and check what commission type line has been applied.
