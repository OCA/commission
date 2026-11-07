- Payments without journal entry (Odoo Enterprise accounting, or
  `account_in_payment` with payment methods without outstanding account)
  have no reconciliation with the invoice until the bank statement line
  is reconciled. Until then their date doesn't limit the settlement, and
  undoing them doesn't set the reversal date, so the negative line takes
  the invoice date.
