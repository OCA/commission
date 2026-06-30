1.  Go to *Invoicing > Configuration > Commissions > Commission types*.
2.  Create a commission and set its *Type* to *Fixed amount per product*.
3.  In the *Product amounts* table, add a line per product with the fixed
    commission amount granted per unit. Optionally set:
    - a *Min. Quantity* to grant a different amount above a quantity threshold
      (add several lines for the same product; the highest applicable
      threshold wins);
    - a *Start Date* / *End Date* to limit the validity of the amount;
    - a *Currency* (the amount is converted to the invoice currency when they
      differ).
4.  Assign this commission to an agent (*Contacts > the agent > Sales &
    Purchase > Commission*). Use a different commission per agent to grant
    different amounts for the same product.
5.  On a customer invoice, the agent is added to the lines and the commission
    is computed as `fixed amount x quantity`, using the line matching the
    invoice date and quantity.

If a product on a posted invoice line has no fixed amount defined in the
agent's commission, posting the invoice is blocked until the amount is
configured.
