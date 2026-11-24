# Copyright 2026 Zhintek - Juan C. Bonilla
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged

MIXIN_NAME = "commission.line.mixin"


@tagged("post_install", "-at_install")
class TestCommissionFormulaMixin(TransactionCase):
    """Test the formula override of ``commission.line.mixin``.

    The mixin is abstract and its ``object_id`` field points to the abstract
    ``commission.mixin``, so no concrete record can be assigned to it. Instead
    of registering a test model, the tests build an in-memory record of the
    mixin itself and patch ``_get_formula_input_dict`` to inject the formula
    context.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mixin = cls.env[MIXIN_NAME]
        cls.formula_source = cls.env["res.partner"].create(
            {"name": "Formula source for tests"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product for formula commission tests"}
        )
        cls.formula_commission = cls.env["commission"].create(
            {
                "name": "Formula commission for tests",
                "commission_type": "formula",
                "formula": 'result = "12.5" if line else "0.0"',
            }
        )
        cls.fixed_commission = cls.env["commission"].create(
            {
                "name": "Fixed commission for tests",
                "commission_type": "fixed",
                "fix_qty": 10.0,
            }
        )

    def _new_line(self):
        """Return an in-memory record of the abstract mixin.

        ``new()`` has no guard against abstract models, so this yields a
        recordset of length 1 and ``ensure_one()`` succeeds. The ``amount``
        field is never read, as its compute raises NotImplementedError.
        """
        return self.mixin.new({})

    @contextmanager
    def _patch_formula_context(self, line):
        """Feed the formula context without touching ``object_id``."""
        with patch.object(
            type(self.mixin),
            "_get_formula_input_dict",
            return_value={"line": self.formula_source, "self": line},
        ):
            yield

    def test_get_formula_input_dict(self):
        line = self._new_line()

        formula_input = line._get_formula_input_dict()

        self.assertEqual(set(formula_input), {"line", "self"})
        self.assertEqual(formula_input["self"], line)
        # object_id is unset on a new record, so it falls back to an empty
        # recordset of its comodel.
        self.assertEqual(formula_input["line"]._name, "commission.mixin")
        self.assertFalse(formula_input["line"])

    def test_get_commission_amount_uses_formula_context(self):
        line = self._new_line()

        with self._patch_formula_context(line):
            amount = line._get_commission_amount(
                self.formula_commission,
                subtotal=100.0,
                product=self.product,
                quantity=1.0,
            )

        # The formula yields a string, the override casts it to float.
        self.assertIsInstance(amount, float)
        self.assertEqual(amount, 12.5)

    def test_get_commission_amount_skips_formula_for_commission_free_product(self):
        line = self._new_line()
        self.product.commission_free = True

        with self._patch_formula_context(line):
            amount = line._get_commission_amount(
                self.formula_commission,
                subtotal=100.0,
                product=self.product,
                quantity=1.0,
            )

        self.assertEqual(amount, 0.0)

    def test_get_commission_amount_without_commission(self):
        line = self._new_line()

        with self._patch_formula_context(line):
            amount = line._get_commission_amount(
                False,
                subtotal=100.0,
                product=self.product,
                quantity=1.0,
            )

        self.assertEqual(amount, 0.0)

    def test_get_commission_amount_delegates_fixed_commission(self):
        line = self._new_line()

        with self._patch_formula_context(line):
            amount = line._get_commission_amount(
                self.fixed_commission,
                subtotal=250.0,
                product=self.product,
                quantity=1.0,
            )

        self.assertEqual(amount, 25.0)
