# Copyright 2021 Andrea Cometa - Apulia Software s.r.l.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def recompute_lines_agents(self):
        for line in self.order_line:
            line.agents = [(6, 0, [])]
            line.agents = line.with_context(
                {'product_id': line.product_id.id}
            )._prepare_agents_vals_partner(self.partner_id)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _prepare_agents_vals_partner(self, partner):
        """Utility method for getting agents of a partner."""
        rec = super(SaleOrderLine, self)._prepare_agents_vals_partner(partner)

        if self._context.get('product_id', False):
            rec = []

            ppa_model = self.env['product.product.agent']
            pca_model = self.env['product.category.agent']

            product = self.env['product.product'].browse(
                self._context['product_id'])

            for agent in partner.agents:
                # default commission_id for agent
                commission_id = agent.commission.id
                commission_id_product = ppa_model.get_commission_id_product(
                    product.id, agent.id)
                if commission_id_product:
                    commission_id = commission_id_product
                else:
                    commission_id_category = pca_model\
                        .get_commission_id_category(
                            product.categ_id, agent.id)
                    if commission_id_category:
                        commission_id = commission_id_category
                rec.append((0, 0, {
                    'agent': agent.id,
                    'commission': commission_id}))
        return rec

    @api.model
    def create(self, vals):
        """Add agents for records created from automations instead of UI."""
        # We use this form as this is the way it's returned when no real vals
        res = super(SaleOrderLine, self).create(vals)
        res.agents = [(6, 0, [])]
        res.agents = (self.with_context(
            {'product_id': res.product_id.id})._prepare_agents_vals_partner(
                res.order_id.partner_id))
        return res
