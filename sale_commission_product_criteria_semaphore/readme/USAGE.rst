To use this module:

#. Install ``sale_commission_product_criteria_semaphore`` together with its
   dependencies.
#. Go to **Commissions > Configuration > Commission types** and open or create a
   commission of type *Product criteria*.
#. Add commission items as usual and optionally set a **Semaphore** value on
   each line:

   * empty semaphore: fallback rule that applies to any line.
   * ``🟢`` success: applies only to green lines.
   * ``🟡`` warning: applies only to yellow lines.
   * ``🔴`` danger: applies only to red lines.

#. When commissions are generated, the module evaluates both the product
   criteria and the semaphore of the source line.
#. Settlement lines keep the semaphore value, and the settlement report shows
   totals grouped by semaphore color.
