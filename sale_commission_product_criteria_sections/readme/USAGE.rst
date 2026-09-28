The commission base amount of the line is matched against the rate sections
of the rule, which are closed intervals: the first section whose limits
contain the base amount is applied, so sections should not overlap.

For example, a rule with these sections:

* 0 - 100: 5%
* 100.01 - 500: 8%
* 500.01 - 1000: 10%

A sale of 200 grants 200 * 8% = 16 of commission and a sale of 600 grants
600 * 10% = 60. A sale of 1500 grants no commission at all, because the base
amount is out of every section.

The base amount is the same used by the other commission types, that is, the
sale amount or, when the commission base is set to "Margin (Amount - Cost)",
the amount without the product cost.
