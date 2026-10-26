This module settles payment based commissions according to the payments
of the invoices:

- An invoice is settled only when its last payment is before the date
  limit of the settlement wizard, the same limit applied to the invoice
  date. Settling a past period later doesn't include the invoices paid
  after that period.
- A payment counts on its due date when it is later than its date, as a
  payment order confirmed before its collection date. Refunds count on
  the reconciliation date.
- Invoices *In Payment* (paid but not matched with the bank yet, as the
  ones included in a payment order) count as paid, as in the base
  module.
- When a payment of an invoice with settled commissions is undone (a
  payment return, removing the payment from the invoice, resetting the
  payment or the invoice to draft), the next settlement includes a
  negative line for the settled amount, dated on the day the payment was
  undone. When the invoice is paid again, a later settlement includes
  the commission again.
