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
