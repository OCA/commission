To use this module, you need to:

* Go to Sales > Commission Management >  Commission Types and create a commission with new Type "Formula".
* Formula is in Python code style

Example:

.. code-block::

  if line._name == 'sale.order.line':
      result = line.price_subtotal * 0.1 + 100
  if line._name == 'account.move.line':
      result = line.price_subtotal * 0.1 + 100

.. code-block::

  line._name == 'sale.order.line'

=> Check the commission is on sale order line object

.. code-block::

    result = line.price_subtotal * 0.1 + 100

=> Commission amount on sale order line  is 10 percent of Sale Order Line Subtotal plus 100

.. code-block::

    if line._name == 'account.move.line':

=> Check the commission is on invoice line object

.. code-block::

    result = line.price_subtotal * 0.1 + 100

=> Commission amount on invoice line is 10 percent of Invoice Line Subtotal amount plus 100
