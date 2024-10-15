# © 2023 ooops404
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr


class SaleCommission(models.Model):
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
            .search([("commission_id", "=", self.id)])
        )
        if items:
            items.write({"active": True})
        return res

    @api.onchange("commission_type")
    def onchange_commission_type(self):
        # Prevent commission_type change in certain cases
        self.check_type_change_allowed_sale()
        self.check_type_change_allowed_moves()

    def check_type_change_allowed_sale(self):
        sola_ids = self.env["sale.order.line.agent"].search(
            [("commission_id", "=", self._origin.id)]
        )
        done_so_ids = sola_ids.filtered(lambda x: x.object_id.state in ["done", "sale"])
        if done_so_ids:
            raise ValidationError(
                _(
                    "There is done Sale Orders with this commission. "
                    "Commission type change is not allowed."
                )
            )

    def check_type_change_allowed_moves(self):
        if not self._origin:
            return
        aila_ids = self.env["account.invoice.line.agent"].search(
            [("commission_id", "=", self._origin.id)]
        )
        done_move_ids = aila_ids.filtered(
            lambda x: x.object_id.parent_state == "posted"
        )
        if done_move_ids:
            raise ValidationError(
                _(
                    "There is posted Account Move Lines with this commission. "
                    "Commission type change is not allowed."
                )
            )


class CommissionItem(models.Model):
    _name = "commission.item"
    _description = "Commission Item"
    _order = "applied_on, based_on, categ_id desc, id desc"

    sequence = fields.Integer(default=10)
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
    percent_amount = fields.Float("Percentage Amount")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
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
        "fixed_amount",
        "percent_amount",
    )
    def _compute_commission_item_name_value(self):
        for item in self:
            if item.categ_id and item.applied_on == "2_product_category":
                item.name = _("Category: %s") % (item.categ_id.display_name)
            elif item.product_tmpl_id and item.applied_on == "1_product":
                item.name = _("Product: %s") % (item.product_tmpl_id.display_name)
            elif item.product_id and item.applied_on == "0_product_variant":
                item.name = _("Variant: %s") % (
                    item.product_id.with_context(
                        display_default_code=False
                    ).display_name
                )
            else:
                item.name = _("All Products")

            if item.commission_type == "fixed":
                decimal_places = self.env["decimal.precision"].precision_get(
                    "Product Price"
                )
                if item.currency_id.position == "after":
                    item.commission_value = "%s %s" % (
                        float_repr(
                            item.fixed_amount,
                            decimal_places,
                        ),
                        item.currency_id.symbol or "",
                    )
                else:
                    item.commission_value = "%s %s" % (
                        item.currency_id.symbol or "",
                        float_repr(
                            item.fixed_amount,
                            decimal_places,
                        ),
                    )
            elif item.commission_type == "percentage":
                item.commission_value = str(item.percent_amount) + " %"

    @api.constrains("product_id", "product_tmpl_id", "categ_id")
    def _check_product_consistency(self):
        for item in self:
            if item.applied_on == "2_product_category" and not item.categ_id:
                raise ValidationError(
                    _(
                        "Please specify the category for which this rule should "
                        "be applied"
                    )
                )
            elif item.applied_on == "1_product" and not item.product_tmpl_id:
                raise ValidationError(
                    _(
                        "Please specify the product for which this rule should "
                        "be applied"
                    )
                )
            elif item.applied_on == "0_product_variant" and not item.product_id:
                raise ValidationError(
                    _(
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
        return super(CommissionItem, self).create(new_values_list)

    def write(self, values):
        values = self.validate_values(values)
        res = super(CommissionItem, self).write(values)
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
