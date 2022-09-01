from odoo.tests.common import TransactionCase


class TestCommission(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission_model = cls.env["commission"]
        cls.res_partner_model = cls.env["res.partner"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.write({"agent": False})
        cls.commission_net_paid = cls.commission_model.create(
            {
                "name": "20% fixed commission (Net amount) - Payment Based",
                "fix_qty": 20.0,
                "invoice_state": "paid",
                "amount_base_type": "net_amount",
            }
        )
        cls.agent_monthly = cls.res_partner_model.create(
            {
                "name": "Test Agent - Monthly",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
                "commission_id": cls.commission_net_paid.id,
            }
        )

    def test_partner_agent_assign(self):
        self.partner.write({"agent_ids": [(4, self.agent_monthly.id)]})
        self.assertEqual(
            self.partner.agent_ids[0].id,
            self.agent_monthly.id,
        )
