from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"  # OCA sale_commission

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        # Method replaced
        if commission.commission_type != "cat_prod_var":
            return super(SaleCommissionLineMixin, self)._get_commission_amount(
                commission, subtotal, product, quantity
            )
        self.ensure_one()
        discount = self.object_id.discount
        if product.commission_free or not commission:
            return 0.0, False
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return 0.0, False
        # Check discount condition
        commission_item = False
        for item_id in item_ids:
            commission_item = self.env["commission.item"].browse(item_id)
            # If both is 0 then discount condition check is disabled
            if commission_item.discount_from + commission_item.discount_to > 0:
                if (
                    commission_item.discount_from
                    <= discount
                    < commission_item.discount_to
                ):
                    break
            else:
                break
            commission_item = False
        if not commission_item:
            return (
                0.0,
                False,
            )  # all commissionitems was rejected because of dicount condition
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        if commission_item.commission_type == "fixed":
            return commission_item.fixed_amount, commission_item
        elif commission_item.commission_type == "percentage":
            return subtotal * (commission_item.percent_amount / 100.0), commission_item

    def _get_commission_items(self, commission, product):
        categ_ids = {}
        categ = product.categ_id
        while categ:
            categ_ids[categ.id] = True
            categ = categ.parent_id
        categ_ids = list(categ_ids)
        # Select all suitable items. Order by best match
        # (priority is: all/cat/subcat/product/variant).
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                commission_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.commission_id = %s)
            ORDER BY
                item.applied_on, categ.complete_name desc, item.id desc
            """,
            (product.product_tmpl_id.ids, product.ids, categ_ids, commission.id),
        )
        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return item_ids


class SaleCommission(models.Model):
    _inherit = "sale.commission"  # OCA

    item_ids = fields.One2many("commission.item", "commission_id")
    commission_type = fields.Selection(
        selection_add=[("cat_prod_var", "By category / product / variant")],
        ondelete={"cat_prod_var": "set default"},
    )


class CommissionItem(models.Model):
    _name = "commission.item"
    _description = "Commission Item"
    _order = "applied_on, categ_id desc, id desc"

    commission_id = fields.Many2one("sale.commission")  # OCA
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
    fixed_amount = fields.Float("Fixed Amount", digits="Product Price")
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
        "Name",
        compute="_compute_commission_item_name_value",
        help="Explicit rule name for this commission line.",
    )
    commission_value = fields.Char(
        "Value",
        compute="_compute_commission_item_name_value",
    )
    discount_from = fields.Float("Discount From")
    discount_to = fields.Float("Discount To")

    @api.constrains("discount_from", "discount_to")
    def _check_discounts(self):
        if any(item.discount_from > item.discount_to for item in self):
            raise ValidationError(
                _("Discount From should be lower than the Discount To.")
            )
        return True

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
                        "Please specify the category for which this rule should be applied"
                    )
                )
            elif item.applied_on == "1_product" and not item.product_tmpl_id:
                raise ValidationError(
                    _(
                        "Please specify the product for which this rule should be applied"
                    )
                )
            elif item.applied_on == "0_product_variant" and not item.product_id:
                raise ValidationError(
                    _(
                        "Please specify the product variant for "
                        "which this rule should be applied"
                    )
                )

    @api.onchange("commission_type")
    def _onchange_compute_price(self):
        if self.commission_type != "fixed":
            self.fixed_amount = 0.0
        if self.commission_type != "percentage":
            self.percent_amount = 0.0

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
    def create(self, vals_list):
        for values in vals_list:
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
        return super(CommissionItem, self).create(vals_list)

    def write(self, values):
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
        res = super(CommissionItem, self).write(values)
        # When the commission changes we need the product.template price
        # to be invalided and recomputed.
        self.flush()
        self.invalidate_cache()
        return res
