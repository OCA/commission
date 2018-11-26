For setting default agents in customers:

#. Go to *Sales > Orders > Customers* or *Contacts > Contacts*.
#. Edit or create a new record.
#. On "Sales & Purchases" page, you will see a field called "Agents" where
   they can be added. You can put the number of agents you want, but you can't
   select specific commission for each partner in this base module.

For adding commissions on sales orders:

#. Go to *Sales > Orders > Quotations*.
#. Edit or create a new record.
#. When you have selected a partner, each new quotation line you add will have
   the agents and commissions set at customer level.
#. You can add, modify or delete these agents discretely clicking on the
   icon with several persons represented, next to the "Commission" field in the
   list. This icon will be available only if the line hasn't been invoiced yet.
#. If you have configured your system for editing lines in a popup window,
   agents will appear also in this window.
#. You have a button "Recompute lines agents" on the bottom of the page
   "Order Lines" for forcing a recompute of all agents from the partner setup.
   This is needed for example when you have changed the partner on the
   quotation having already inserted lines.

For adding commissions on invoices:

#. Go to *Invoicing > Sales > Customer Invoices*.
#. Follow the same steps as in sales orders.
#. The agents icon will be in this ocassion visible when the line hasn't been
   settled.
#. Take into account that invoices sales orders will transfer agents
   information when being invoiced.

For settling the commissions to agents:

#. Go to *Sales > Commissions Management > Settle commissions*.
#. On the window that appears, you should select the date up to which you
   want to create commissions. It should be at least one day after the last
   period date. For example, if you settlements are monthly, you have to put
   at least the first day of the following month.
#. You can settle only certain agents if you select them on the "Agents"
   section. Leave it empty for settling all.
#. Click on "Make settlements" button.
#. If there are new settlements, they will be shown after this.

For invoicing the settlements (only for external agents):

#. Go to *Sales > Commissions Management > Create commission invoices*.
#. On the window that appears, you can select following data:

   * Product. It should be a service product for being coherent.
   * Journal: To be selected between existing purchase journals.
   * Date: If you want to choose a specific invoice date. You can leave it
     blank if you prefer.
   * Settlements: For selecting specific settlements to invoice. You can leave
     it blank as well for invoicing all the pending settlements.

#. If you want to invoice a specific settlement, you can navigate to it in
   *Sales > Commissions Management > Settlements*, and click on "Make invoice"
   button.
