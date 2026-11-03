# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user

from .test_commission import TestCommissionBase


class TestCommissionSecurity(TestCommissionBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create(
            {"name": "Other commission company"}
        )
        cls.commission_user = new_test_user(
            cls.env,
            login="commission_user",
            groups="commission_oca.group_commission_user",
            company_id=cls.company.id,
            company_ids=[Command.set((cls.company | cls.other_company).ids)],
        )
        cls.commission_manager = new_test_user(
            cls.env,
            login="commission_manager",
            groups="commission_oca.group_commission_manager",
            company_id=cls.company.id,
            company_ids=[Command.set((cls.company | cls.other_company).ids)],
        )
        cls.internal_user = new_test_user(
            cls.env,
            login="commission_internal_user",
            groups="base.group_user",
            company_id=cls.company.id,
        )
        cls.settlement = cls.settle_model.create(
            {
                "agent_id": cls.agent_monthly.id,
                "date_from": "2026-01-01",
                "date_to": "2026-01-31",
                "company_id": cls.company.id,
            }
        )
        cls.other_settlement = cls.settlement.copy({"company_id": cls.other_company.id})

    def test_model_permissions(self):
        for model_name in (
            "commission",
            "commission.section",
            "commission.settlement",
            "commission.settlement.line",
            "commission.make.settle",
        ):
            for user in (
                self.internal_user,
                self.commission_user,
                self.commission_manager,
            ):
                model = (
                    self.env[model_name]
                    .with_user(user)
                    .with_context(allowed_company_ids=self.company.ids)
                )
                for operation in ("read", "write", "create", "unlink"):
                    with self.subTest(
                        model=model_name, user=user.login, operation=operation
                    ):
                        if user == self.commission_manager:
                            expected = not (
                                model_name == "commission.make.settle"
                                and operation == "unlink"
                            )
                        else:
                            expected = (
                                user == self.commission_user
                                and model_name != "commission.make.settle"
                                and operation == "read"
                            )
                        self.assertEqual(model.has_access(operation), expected)

    def test_settlement_multi_company_read(self):
        settlements = self.settlement | self.other_settlement
        for user in (self.commission_user, self.commission_manager):
            model = self.settle_model.with_user(user).with_context(
                allowed_company_ids=self.company.ids
            )
            with self.subTest(user=user.login):
                self.assertEqual(
                    model.search([("id", "in", settlements.ids)]).ids,
                    self.settlement.ids,
                )
                with self.assertRaises(AccessError):
                    self.other_settlement.with_env(model.env).read(["date_from"])
                self.assertEqual(
                    set(
                        model.with_context(
                            allowed_company_ids=(self.company | self.other_company).ids
                        )
                        .search([("id", "in", settlements.ids)])
                        .ids
                    ),
                    set(settlements.ids),
                )

    def test_settlement_multi_company_manager_operations(self):
        model = self.settle_model.with_user(self.commission_manager).with_context(
            allowed_company_ids=self.company.ids
        )
        own = self.settlement.with_env(model.env)
        other = self.other_settlement.with_env(model.env)
        for operation in ("read", "write", "create", "unlink"):
            with self.subTest(operation=operation):
                self.assertTrue(own.has_access(operation))
                self.assertFalse(other.has_access(operation))
        with self.assertRaises(AccessError), self.cr.savepoint():
            other.write({"name": "Forbidden change"})
        with self.assertRaises(AccessError), self.cr.savepoint():
            other.unlink()
        values = {
            "agent_id": self.agent_monthly.id,
            "date_from": "2026-02-01",
            "date_to": "2026-02-28",
            "company_id": self.other_company.id,
        }
        with self.assertRaises(AccessError), self.cr.savepoint():
            model.create(values)
        values["company_id"] = self.company.id
        settlement = model.create(values)
        settlement.write({"name": "Allowed change"})
        settlement.unlink()
