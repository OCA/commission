1.  Go to Commissions \> Configuration \> Commission Types.
2.  Create a Commission Type with type = "Product criteria".
3.  Create multiple rules based on variant/product/category or global.
4.  On each rule, optionally set:
    - **Per unit** (for fixed-amount rules): multiply the amount by the
      line quantity, expressed in the default unit of measure of the
      product.
    - **Min. Quantity**: only apply this rule when the line quantity,
      expressed in the default unit of measure of the product, is at or
      above this threshold. A rule without minimum quantity always
      applies; when several rules match at the same level, the one with
      the highest applicable minimum quantity is used.
    - **Start Date / End Date**: restrict the rule to a date range,
      evaluated against the invoice date, or against the order date in the
      timezone of the company.

A rule only applies to the orders and the invoices of its company. Leave
its **Company** empty to share it with every company.

Fixed amounts are set in the currency of the company of the rule and
converted to the currency of the order or the invoice at its date. A rule
shared by every company has no currency of its own, so its amount is taken
in the currency of the company of the order or the invoice.

Editing a rule does not recompute the commissions already computed on
existing orders and invoices, so that settled amounts stay untouched. Use
the *Regenerate agents* button on a draft order or invoice to apply the
current rules to it.

When the commission is based on the net amount, the product cost is
subtracted per unit of the default unit of measure of the product too, and
converted from the currency of the company the same way.
