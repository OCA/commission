from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.depends("message_follower_ids")
    def _get_followers(self):
        super()._get_followers()
        for thread in self:
            if thread._name == "res.partner" and thread.agent:
                if thread.user_ids.has_group(
                    "sale_commission_agent_restrict.group_agent_own_customers"
                ):
                    thread.sudo().message_partner_ids = False
                    thread.sudo().message_channel_ids = False
