# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _


class ResPartnerAgent(models.Model):
    """This model relates sales agents to partnes"""
    _name = "res.partner.agent"
    _rec_name = "agent_name"

    partner_id = fields.Many2one("res.partner", required=True,
                                 ondelete="cascade", select=1)
    agent_id = fields.Many2one("sale.agent", string="Agent", required=True,
                               ondelete="cascade")
    agent_name = fields.Char(string="Agent name", related="agent_id.name")
    commission_id = fields.Many2one("commission", string="Applied commission",
                                    required=True, ondelete="cascade")
    agent_type = fields.Selection(string="Type", related="agent_id.agent_type",
                                  selection=[('adviser', 'Adviser'),
                                             ('commercial', 'Commercial')],
                                  readonly=True, store=True)

    @api.onchange("agent_id")
    def do_set_default_commission(self):
        """Set default commission when sale agent has changed"""
        self.commission_id = self.agent_id.commission

    @api.onchange("commission_id")
    def do_check_commission(self):
        """Check selected commission and raise a warning
        when selected commission is not the default provided for sale agent
        and default partner commission have sections
        """
        commission = self.commission_id
        if commission.id:
            agent_commission = self.agent_id.commission
            if self.agent_id and commission.sections:
                if commission != agent_commission:
                    return {
                        "warning": {
                            "title": _('Fee installments!'),
                            "message": _(
                                "Selected commission has been assigned "
                                "by sections and it does not match "
                                "the one defined to the selected agent."
                                "These sections shall apply only on this bill."
                            )
                        }
                    }
