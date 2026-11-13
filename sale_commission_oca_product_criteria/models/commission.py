# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import formatLang


class Commission(models.Model):
    _inherit = "commission"

    commission_type = fields.Selection(
        selection_add=[("product", "Product criteria")],
        ondelete={"product": "set default"},
    )
    item_ids = fields.One2many("commission.item", "commission_id", copy=True)

    def action_unarchive(self):
        res = super().action_unarchive()
        items = (
            self.env["commission.item"]
            .with_context(active_test=False)
            .search([("commission_id", "in", self.ids)])
        )
        if items:
            items.action_unarchive()
        return res

    def write(self, values):
        if "commission_type" in values:
            # Only the records whose type the write really changes: write()
            # validates every key it is given, changed or not, so a constraint
            # would also reject an import or a data file rewriting the type
            # with the value it already holds.
            self.filtered(
                lambda x: x.commission_type != values["commission_type"]
            )._check_type_change_allowed()
        return super().write(values)

    def _check_type_change_allowed(self):
        """Prevent the type change once the commission has been applied.

        Checked on write rather than through an onchange, as the amounts
        already computed with the previous type are kept whatever writes the
        field: the form, an import, an automation or another module.
        """
        self.check_type_change_allowed_sale()
        self.check_type_change_allowed_moves()

    def check_type_change_allowed_sale(self):
        # Sudoed, as an applied commission has to block the type change even
        # when the documents it is applied on belong to another company or to
        # a salesperson the user writing the type is not allowed to see.
        sola_ids = (
            self.env["sale.order.line.agent"]
            .sudo()
            .search([("commission_id", "in", self.ids)])
        )
        done_so_ids = sola_ids.filtered(lambda x: x.object_id.state in ["done", "sale"])
        if done_so_ids:
            raise ValidationError(
                self.env._(
                    "There is done Sale Orders with this commission. "
                    "Commission type change is not allowed."
                )
            )

    def check_type_change_allowed_moves(self):
        aila_ids = (
            self.env["account.invoice.line.agent"]
            .sudo()
            .search([("commission_id", "in", self.ids)])
        )
        done_move_ids = aila_ids.filtered(
            lambda x: x.object_id.parent_state == "posted"
        )
        if done_move_ids:
            raise ValidationError(
                self.env._(
                    "There is posted Account Move Lines with this commission. "
                    "Commission type change is not allowed."
                )
            )


class CommissionItem(models.Model):
    _name = "commission.item"
    _description = "Commission Item"
    _order = "applied_on, min_qty desc, based_on, categ_id desc, sequence, id desc"

    sequence = fields.Integer(
        default=10,
        help="Order in which the rules matching equally well are evaluated: "
        "the lowest sequence is the one that applies.",
    )
    active = fields.Boolean(default=True)
    commission_id = fields.Many2one(
        "commission",
        string="Commission",
        domain=[("commission_type", "=", "product")],
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        "Product",
        ondelete="cascade",
        check_company=True,
        help="Specify a template if this rule only applies to one "
        "product template. Keep empty otherwise.",
    )
    product_id = fields.Many2one(
        "product.product",
        "Product Variant",
        ondelete="cascade",
        check_company=True,
        help="Specify a product if this rule only applies "
        "to one product. Keep empty otherwise.",
    )
    categ_id = fields.Many2one(
        "product.category",
        "Product Category",
        ondelete="cascade",
        help="Specify a product category if this rule only applies to "
        "products belonging to this category or its children categories. "
        "Keep empty otherwise.",
    )
    based_on = fields.Selection(
        [("sol", "Any Sale Order Line")],
        required=True,
        default="sol",
    )
    applied_on = fields.Selection(
        [
            ("3_global", "All Products"),
            ("2_product_category", "Product Category"),
            ("1_product", "Product"),
            ("0_product_variant", "Product Variant"),
        ],
        "Apply On",
        default="3_global",
        required=True,
        help="Commission Item applicable on selected option",
    )
    commission_type = fields.Selection(
        [("fixed", "Fixed"), ("percentage", "Percentage")],
        index=True,
        default="fixed",
        required=True,
    )
    fixed_amount = fields.Float(digits="Product Price")
    per_unit = fields.Boolean(
        help="When checked, the fixed commission amount is multiplied by "
        "the quantity on the sale/invoice line.\n"
        "Expressed in the default unit of measure of the product.",
    )
    percent_amount = fields.Float("Percentage Amount")
    min_qty = fields.Float(
        string="Min. Quantity",
        default=0.0,
        digits="Product Unit",
        help="Minimum quantity on the sale/invoice line for this rule to "
        "apply. When several rules match, the one with the highest "
        "applicable minimum quantity is used.\n"
        "Expressed in the default unit of measure of the product.",
    )
    date_start = fields.Date(
        help="Start date for this rule (inclusive). Leave empty for no "
        "start date restriction.",
    )
    date_end = fields.Date(
        help="End date for this rule (inclusive). Leave empty for no "
        "end date restriction.",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        help="Company this rule applies to. Leave empty to share it with "
        "every company.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        help="Currency the fixed amount of the rule is expressed in. A rule "
        "shared by every company has none, as its amount is then taken in "
        "the currency of the company of the order or the invoice.",
    )
    name = fields.Char(
        compute="_compute_commission_item_name_value",
        help="Explicit rule name for this commission line.",
    )
    commission_value = fields.Char(
        "Value",
        compute="_compute_commission_item_name_value",
    )

    @api.depends(
        "applied_on",
        "categ_id",
        "product_tmpl_id",
        "product_id",
        "commission_type",
        "currency_id",
        "fixed_amount",
        "per_unit",
        "percent_amount",
    )
    def _compute_commission_item_name_value(self):
        for item in self:
            if item.categ_id and item.applied_on == "2_product_category":
                item.name = self.env._(
                    "Category: %(name)s", name=item.categ_id.display_name
                )
            elif item.product_tmpl_id and item.applied_on == "1_product":
                item.name = self.env._(
                    "Product: %(name)s", name=item.product_tmpl_id.display_name
                )
            elif item.product_id and item.applied_on == "0_product_variant":
                item.name = self.env._(
                    "Variant: %(name)s",
                    name=item.product_id.with_context(
                        display_default_code=False
                    ).display_name,
                )
            else:
                item.name = self.env._("All Products")
            if item.commission_type == "fixed":
                # A rule shared by every company has no currency of its own,
                # so its amount is displayed without any currency symbol.
                value = formatLang(
                    self.env,
                    item.fixed_amount,
                    dp="Product Price",
                    currency_obj=item.currency_id,
                )
                item.commission_value = (
                    self.env._("%(value)s / unit", value=value)
                    if item.per_unit
                    else value
                )
            else:
                item.commission_value = f"{item.percent_amount} %"

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for item in self:
            if item.date_start and item.date_end and item.date_start > item.date_end:
                raise ValidationError(
                    self.env._("The start date cannot be after the end date.")
                )

    @api.constrains("applied_on", "product_id", "product_tmpl_id", "categ_id")
    def _check_product_consistency(self):
        for item in self:
            if item.applied_on == "2_product_category" and not item.categ_id:
                raise ValidationError(
                    self.env._(
                        "Please specify the category for which this rule should "
                        "be applied"
                    )
                )
            elif item.applied_on == "1_product" and not item.product_tmpl_id:
                raise ValidationError(
                    self.env._(
                        "Please specify the product for which this rule should "
                        "be applied"
                    )
                )
            elif item.applied_on == "0_product_variant" and not item.product_id:
                raise ValidationError(
                    self.env._(
                        "Please specify the product variant for "
                        "which this rule should be applied"
                    )
                )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        has_product_id = self.filtered("product_id")
        for item in has_product_id:
            item.product_tmpl_id = item.product_id.product_tmpl_id
        if self.env.context.get("default_applied_on", False) == "1_product":
            # If a product variant is specified, apply on variants instead
            # Reset if product variant is removed
            has_product_id.update({"applied_on": "0_product_variant"})
            (self - has_product_id).update({"applied_on": "1_product"})

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self):
        has_tmpl_id = self.filtered("product_tmpl_id")
        for item in has_tmpl_id:
            if (
                item.product_id
                and item.product_id.product_tmpl_id != item.product_tmpl_id
            ):
                item.product_id = None

    @api.model_create_multi
    def create(self, values_list):
        new_values_list = []
        for values in values_list:
            values = self.validate_values(values)
            new_values_list.append(values)
        return super().create(new_values_list)

    def write(self, values):
        values = self.validate_values(values)
        res = super().write(values)
        return res

    def validate_values(self, values):
        if values.get("applied_on", False):
            # Ensure item consistency for later searches.
            applied_on = values["applied_on"]
            if applied_on == "3_global":
                values.update(
                    dict(product_id=None, product_tmpl_id=None, categ_id=None)
                )
            elif applied_on == "2_product_category":
                values.update(dict(product_id=None, product_tmpl_id=None))
            elif applied_on == "1_product":
                values.update(dict(product_id=None, categ_id=None))
            elif applied_on == "0_product_variant":
                values.update(dict(categ_id=None))
        return values
