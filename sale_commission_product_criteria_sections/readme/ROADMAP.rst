The amount of a commission item is computed by the
``_get_commission_item_amount()`` hook of ``commission.line.mixin``, which
is provided by ``sale_commission_product_criteria``.

Every module of the product criteria family that computes the amount of a
commission item must use that hook instead of overriding
``_get_single_commission_amount()``, otherwise the commission types of the
other modules are silently ignored. In particular,
``sale_commission_product_criteria_discount`` computes the amount of the
commission items with it, so both modules can be installed at the same time.
