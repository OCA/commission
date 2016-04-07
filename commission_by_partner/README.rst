.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Sales commissions by partner
=================

This module allows to define different agents and commissions by partner.

In partner form view we can define several agents with specific commissions to
each partner instead several agents with the same default commission defined in
the agent.


Known issues / Roadmap
======================
If previous data of field 'agents' in res.partner exists it will be coppied
into the new field 'commission_ids'.

If no default commission defined in the partners agents then will no be coppied
into 'commission_ids' field.

The field agents from sale_commission module will be invisible.


Credits
=======

Contributors
------------
* Comunitea
* Javier Colmenero <javier@comunitea.com>

Icon
----
* https://openclipart.org/detail/43969/pile-of-golden-coins-by-j_alves

Maintainer
----------
This module is maintained by Comunitea.