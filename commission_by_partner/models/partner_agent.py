# -*- coding: utf-8 -*-
# © 2015 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# © 2015 Javier Colmenero Fernández (<javier@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from openerp import _


class ResPartnerAgent(models.Model):
    """
    Relation between partner and agents.
    """
    _name = "res.partner.agent"

    @api.model
    def _get_default_company_id(self):
        company_obj = self.env['res.company']
        company_id = company_obj._company_default_get('res.partner.agent')
        return company_obj.browse(company_id)

    partner_id = fields.Many2one('res.partner', 'Partner', required=True,
                                 ondelete='cascade', help='', select=1)
    agent_id = fields.Many2one('res.partner', 'Agent', required=True,
                               ondelete='cascade', help='',
                               domain="[('agent', '=', True)]")
    commission_id = fields.Many2one('sale.commission', 'Applied commission',
                                    required=True, help='')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=_get_default_company_id)

    def name_get(self, cr, uid, ids, context=None):
        """devuelve como nombre del agente del partner el nombre del agente"""
        if context is None:
            context = {}
        res = []
        for obj in self:
            res.append((obj.id, obj.agent_id.name))

        return res

    @api.onchange('agent_id')
    def onchange_agent_id(self):
        if self.agent_id:
            self.commission = self.agent_id.commission.id

    @api.onchange('commission_id', 'agent_id')
    def onchange_commission_id(self):
        res = {}
        if self.commission_id and self.commission_id.sections \
                and self.agent_id:
            if self.agent_id.commission.id != self.commission_id.id:
                res['warning'] = {}
                res['warning']['title'] = _('Fee installments!')
                res['warning']['message'] = _(
                    'A commission has been assigned by sections that '
                    'does not match that defined for the agent by '
                    'default, so that these sections shall apply '
                    'only on this bill.')
        return res
