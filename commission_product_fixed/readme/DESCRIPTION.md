This module adds a new commission type, **Fixed amount per product**, on top
of the OCA commission framework.

Instead of computing the commission as a percentage of the sale/invoice amount
or the margin, the commission is a fixed amount defined per product. The amount
is independent from the selling price.

Because each agent is assigned its own commission, the same product can grant a
different fixed amount depending on the agent: just define a separate commission
per agent with its own per-product amounts.
