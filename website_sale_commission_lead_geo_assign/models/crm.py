# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def geo_assign_agents(self, check_existing_agents=True, leads=None):
        """Assign an agent to the leads specified.
        :param leads: Recordset of leads to assign.
        :param check_existing_agents:
            See the homonym parameter in geo_assign_lead.
        """
        if not leads:
            leads = self.search([])
        wiz = self.env['wizard.geo.assign.lead'].create({
            'check_existing_agents': check_existing_agents
        })
        wiz.with_context(active_ids=leads.ids).geo_assign_lead()

    @api.model
    def create(self, vals):
        lead = super(Lead, self).create(vals)
        self.geo_assign_agents(leads=lead)
        return lead
