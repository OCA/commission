# Copyright 2025 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CommissionItem(models.Model):
    _inherit = "commission.item"

    commission_type = fields.Selection(
        selection_add=[("section", "By sections")],
        ondelete={"section": "set default"},
    )
    section_ids = fields.One2many(
        comodel_name="commission.section",
        inverse_name="commission_item_id",
        string="Sections",
        copy=True,
    )

    def _compute_commission_item_name_value(self):
        res = super()._compute_commission_item_name_value()
        for item in self.filtered(lambda x: x.commission_type == "section"):
            item.commission_value = _("By sections")
        return res

    def _calculate_section_amount(self, base):
        """Return the commission amount for ``base``, following the sections.

        Sections are closed intervals, so the first one whose ``amount_from``
        and ``amount_to`` contain ``base`` is applied. They are evaluated by
        sequence, so the precedence between overlapping sections is explicit.
        Zero is returned when no section matches ``base``.

        It mirrors ``commission.calculate_section()``, which applies the
        sections of a commission instead of the ones of a commission item.
        """
        self.ensure_one()
        section = self.section_ids.filtered(
            lambda x: x.amount_from <= base <= x.amount_to
        )[:1]
        if not section:
            return 0.0
        return base * section.percent / 100.0


class CommissionSection(models.Model):
    _inherit = "commission.section"

    # The sections are applied by order, so the sequence defines which one
    # is applied when several of them match the same amount.
    _order = "sequence, id"

    commission_item_id = fields.Many2one(
        comodel_name="commission.item",
        string="Commission Item",
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)

    @api.constrains("commission_id", "commission_item_id")
    def _check_section_parent(self):
        for section in self:
            if bool(section.commission_id) == bool(section.commission_item_id):
                raise ValidationError(
                    _(
                        "A section belongs either to a commission or to a "
                        "commission item, but not to both of them."
                    )
                )
