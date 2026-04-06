1. Open a lead or opportunity in the CRM.
2. In the **Agents** field, select one or more commission agents.
3. When converting the lead to an opportunity:

   - **Create a new customer**: the new partner will be created with the
     agents already assigned.
   - **Link to an existing customer**: the agents will be added to the
     existing partner (without duplicating agents already present).

4. Any sale order created for that partner will automatically inherit the
   commission agents on its lines (via ``sale_commission_oca``).
