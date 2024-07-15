The module allows you to integrate check deposit with agent commissions.

When generating agent settlements, select a
payment date until which commissions should be settled.

Invoices with checks payment will be taken
into consideration only if the number of
days set in the "Safety days for commission"
field in journal configuration from due date
set in check payment have passed from settlement payment date.

Eg:

- Invoice 0001 is paid with check
- Check due date: January 1st
- "Safety days for commission" set in check journal: 10
- In settlement wizard:
    - Settle commissions until payment date: January 5th => commission is not settled for check
    - Settle commissions until payment date: January 15th => commission is settled for check
