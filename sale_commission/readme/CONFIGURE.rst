For adding commissions:

#. Go to *Sales > Commission Management > Commission types*.
#. Edit or create a new record.
#. Select a name for distinguishing that type.
#. Select the percentage type of the commission:

   * **Fixed percentage**: all commissions are computed with a fixed
     percentage. You can fill the percentage in the field "Fixed percentage".
   * **By sections**: percentage varies depending amount intervals. You can
     fill intervals and percentages in the section "Rate definition".

#. Select the base amount for computing the percentage:

   * **Gross Amount**: percentage is computed from the amount put on
     sales order/invoice.
   * **Net Amount**: percentage is computed from the profit only, taken the
     cost from the product.

#. Select the invoice status for settling the commissions:

   * **Invoice Based**: Commissions are settled when the invoice is issued.
   * **Payment Based**: Commissions are settled when the invoice is paid.

For adding new agents:

#. Go to *Sales > Commission Management > Agents*. You can also access from
   *Contacts > Contacts* or *Sales > Orders > Customers*.
#. Edit or create a new record.
#. On "Sales & Purchases" page, mark "Agent" check. It should be checked if
   you have accessed from first menu option.
#. There's a new page called "Agent information". In it, you can set following
   data:

   * The agent type, being in this base module "External agent" the only
     existing configuration. It can be extended with `hr_commission` module
     for setting an "Employee" agent type.
   * The associated commission type.
   * The settlement period, where you can select:
   *
     * Monthly: the settlement will be done for the whole past month.
     * Bi-weekly: there will be 2 settlement per month, one covering the first
       15 days, and the other for the rest of the month.
     * Quaterly: the settlement will cover a quarter of the year (3 months).
     * Semi-annual: there will be 2 settlements for each year, each one
       covering 6 months.
     * Annual: only one settlement per year.

   You will also be able to see the settlements that have been made to this
   agent from this page.
