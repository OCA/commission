# Copyright 2016-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class Commission(models.Model):
    _name = "commission"
    _description = "Commission"

    name = fields.Char(required=True)
    commission_type = fields.Selection(
        selection=[
            ("fixed", "Fixed percentage"),
            ("section", "By sections"),
        ],
        string="Type",
        required=True,
        default="fixed",
        help="Select the percentage type of the commission:\n"
        "* 'Fixed percentage': all commissions are computed with a fixed percentage. "
        'You can fill the percentage in the field "Fixed percentage".\n'
        "* 'By sections': percentage varies depending on detailed conditions.",
    )
    use_range = fields.Boolean(
        default=True, help='You can fill intervals in the section "Rate definition".'
    )
    fix_qty = fields.Float(string="Fixed percentage")
    section_ids = fields.One2many(
        string="Sections",
        comodel_name="commission.section",
        inverse_name="commission_id",
    )
    active = fields.Boolean(default=True)
    amount_base_type = fields.Selection(
        selection=[
            ("gross_amount", "Sale/Invoice Amount"),
            ("net_amount", "Margin (Amount - Cost)"),
        ],
        string="Base",
        required=True,
        default="gross_amount",
        help="Select the base amount for computing the percentage:\n"
        "* 'Sale/Invoice Amount': percentage is computed from "
        "the amount put on sales order/invoice.\n"
        "* 'Margin (Amount - Cost)': percentage is computed from "
        "the profit only, taken the cost from the product.",
    )
    settlement_type = fields.Selection(selection="_selection_settlement_type")

    @api.model
    def _selection_settlement_type(self):
        """Return the same types as the settlements."""
        return self.env["commission.settlement"].fields_get(
            allfields=["settlement_type"]
        )["settlement_type"]["selection"]

    @api.model
    def _get_included_sections_domain(self, base, record):
        if not record:
            return [(1, "=", 0)]
        return [
            "&",
            "|",
            "|",
            ("product_id", "=", record.product_id.id),
            ("category_id", "child_of", record.product_id.categ_id.id),
            "&",
            ("product_id", "=", False),
            ("category_id", "=", False),
            "|",
            ("commission_id.use_range", "=", False),
            "&",
            ("amount_from", "<=", base),
            ("amount_to", ">=", base),
        ]

    def calculate_section(self, base, record=False):
        self.ensure_one()
        section = self.section_ids.filtered_domain(
            self._get_included_sections_domain(base, record)
        )[:1]
        if section:
            return base * section.percent / 100.0
        return 0.0


class CommissionSection(models.Model):
    _name = "commission.section"
    _description = "Commission section"
    _order = "product_id desc, category_complete_name desc, id asc"

    commission_id = fields.Many2one("commission", string="Commission")
    amount_from = fields.Float(string="From")
    amount_to = fields.Float(string="To")
    category_id = fields.Many2one("product.category")
    category_complete_name = fields.Char(
        related="category_id.complete_name", store=True
    )
    product_id = fields.Many2one("product.product")
    percent = fields.Float(required=True)

    @api.constrains("amount_from", "amount_to")
    def _check_amounts(self):
        for section in self:
            if (
                section.commission_id.use_range
                and section.amount_to < section.amount_from
            ):
                raise exceptions.ValidationError(
                    _("The lower limit cannot be greater than upper one.")
                )
