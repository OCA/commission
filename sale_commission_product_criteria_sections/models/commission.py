from odoo import _, fields, models


class CommissionItem(models.Model):
    _inherit = "commission.item"

    commission_type = fields.Selection(
        selection_add=[("section", _("By sections"))],
        ondelete={"section": "set default"},
    )
    section_ids = fields.One2many(
        "commission.section",
        "commission_item_id",
        string="Sections",
        copy=True,
    )

    def _compute_commission_item_name_value(self):
        res = super()._compute_commission_item_name_value()
        for item in self:
            if item.commission_type == "section":
                item.commission_value = _("By sections")
        return res

    def _calculate_section_amount(self, base):
        for section in self.section_ids:
            if section.amount_from <= base <= section.amount_to:
                return base * section.percent / 100.0
        return 0.0


class CommissionSection(models.Model):
    _inherit = "commission.section"

    commission_item_id = fields.Many2one(
        "commission.item",
        string="Commission Item",
        ondelete="cascade",
    )
