This module bridges the CRM and commission modules by allowing commission
agents to be assigned directly on leads and opportunities.

When a lead is converted into an opportunity and a customer is created or
linked, the agents defined on the lead are automatically propagated to the
partner's ``agent_ids`` field. This ensures that sale orders generated from
that opportunity will inherit the correct commission agents through the
standard ``sale_commission_oca`` computation.
