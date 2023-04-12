from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr

COMMISSION_ITEM_TYPES = {
    "0_product_variant": 1000,
    "1_product": 10000,
    "2_product_category": 100000,
    "3_global": 1000000,
}


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"  # OCA sale_commission

    commission_ids = fields.Many2many("sale.commission", string="Commissions")
    applied_commission_id = fields.Many2one("sale.commission", readonly=True)
    commission_id = fields.Many2one(
        comodel_name="sale.commission",
        ondelete="restrict",
        required=False,
        compute="_compute_commission_id",
        store=True,
        readonly=False,
        copy=True,
    )

    def _get_commission_amount(
        self, commission, commissions, subtotal, product, quantity
    ):
        # Method replaced
        if commissions:
            return self._get_multi_commission_amount(
                commissions, subtotal, product, quantity
            )
        elif commission:
            return self._get_single_commission_amount(
                commission, subtotal, product, quantity
            )

    def _get_commission_items(self, commission, product):
        # Method replaced
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
            (
                product.product_tmpl_id.ids,
                product.ids,
                categ_ids,
                commission._origin.id,  # Added this
            ),
        )
        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return item_ids

    def _get_multi_commission_amount(self, commissions, subtotal, product, quantity):
        for com in commissions.sorted("sequence"):
            amount = self._get_single_commission_amount(
                com, subtotal, product, quantity
            )
            if amount > 0:
                # self.commission_ids = [(5, 0, 0)]
                self.applied_commission_id = com.id
                return amount
        return 0

    def _get_single_commission_amount(self, commission, subtotal, product, quantity):
        self.ensure_one()
        if product.commission_free or not commission:
            return 0.0
        item_ids = self._get_commission_items(commission, product)
        if not item_ids:
            return 0.0
        # Check discount condition
        commission_item = False
        for item_id in item_ids:
            commission_item = self.env["commission.item"].browse(item_id)
            discount = self._get_discount_value(commission_item)
            if commission_item.based_on != "sol":
                if (
                    commission_item.discount_from
                    <= discount
                    <= commission_item.discount_to
                ):
                    break
            else:
                break
            commission_item = False
        if not commission_item:
            # all commission items was rejected
            return 0.0
        if commission.amount_base_type == "net_amount":
            # If subtotal (sale_price * quantity) is less than
            # standard_price * quantity, it means that we are selling at
            # lower price than we bought, so set amount_base to 0
            subtotal = max([0, subtotal - product.standard_price * quantity])
        self.applied_commission_item_id = commission_item
        # if self.agent_id.use_multi_type_commissions:
        self.applied_commission_id = commission_item.commission_id
        if commission_item.commission_type == "fixed":
            return commission_item.fixed_amount
        elif commission_item.commission_type == "percentage":
            return subtotal * (commission_item.percent_amount / 100.0)

    def _get_discount_value(self, commission_item):
        # Will be overridden
        # commission_item will be used only in ooops_sale_commission_absolute_discount
        # sale_commission_triple_discount will always use line final discount
        return self.object_id.discount


class AccountInvoiceLineAgent(models.AbstractModel):
    _inherit = "account.invoice.line.agent"

    applied_commission_item_id = fields.Many2one("commission.item")

    @api.depends(
        "object_id.price_subtotal",
        "object_id.product_id.commission_free",
        "commission_id",
    )
    def _compute_amount(self):
        for line in self:
            inv_line = line.object_id
            line.amount, line.applied_commission_item_id = line._get_commission_amount(
                line.commission_id,
                inv_line.price_subtotal,
                inv_line.product_id,
                inv_line.quantity,
                inv_line.discount,
            )
            # Refunds commissions are negative
            if line.invoice_id.move_type and "refund" in line.invoice_id.move_type:
                line.amount = -line.amount


class SaleCommission(models.Model):
    _inherit = "sale.commission"

    use_discount_in_ct_lines = fields.Boolean(
        "Use Discounts in Commission Rules", compute="_compute_use_discount_in_ct_lines"
    )
    commission_type = fields.Selection(
        selection_add=[("rules", "Rules")], ondelete={"rules": "cascade"}
    )
    item_ids = fields.One2many("commission.item", "commission_id")
    sequence = fields.Integer(
        "Sequence", default=1, help="The first in the sequence is the default one."
    )

    def _compute_use_discount_in_ct_lines(self):
        for rec in self:
            rec.use_discount_in_ct_lines = self.env.company.use_discount_in_ct_lines

    def write(self, vals):
        res = super(SaleCommission, self).write(vals)
        self.sort_items()
        return res

    def sort_items(self):
        # Priority 1: product_variant > product > product_category > global
        # Priority 2 (inside of priority 1):
        # Discount > SOL
        # Priority 3 (inside of priority 2):
        # Regular with price list > Regular without price list
        for com_type, seq in COMMISSION_ITEM_TYPES.items():
            all_lines = self.item_ids.filtered(lambda x: x.applied_on == com_type)

            sol_lines = all_lines.filtered(lambda x: x.based_on == "sol")
            sol_lines_no_price_list = sol_lines.filtered(lambda x: not x.pricelist_id)
            sol_lines_price_list = sol_lines.filtered(lambda x: x.pricelist_id)

            disc_lines = all_lines.filtered(lambda x: x.based_on == "discount")
            disc_lines_no_price_list = disc_lines.filtered(lambda x: not x.pricelist_id)
            disc_lines_price_list = disc_lines.filtered(lambda x: x.pricelist_id)

            disc_lines_price_list.update({"sequence": seq + 10})
            disc_lines_no_price_list.update({"sequence": seq + 11})

            sol_lines_price_list.update({"sequence": seq + 100})
            sol_lines_no_price_list.update({"sequence": seq + 101})


class AgentCommission(models.Model):
    _name = "agent.commission"
    _description = "Agent Commission"

    sequence = fields.Integer(default=10)
    agent_id = fields.Many2one(
        "res.partner",
        domain=[("agent", "=", True)],
        required=True,
    )
    commission_id = fields.Many2one(
        "sale.commission", string="Commission", required=True
    )
    name = fields.Char(compute="_compute_agent_name", store=True, index=True)

    @api.depends("agent_id", "commission_id")
    def _compute_agent_name(self):
        for r in self:
            if r.agent_id and r.commission_id:
                r.name = r.agent_id.name + " " + r.commission_id.name
            else:
                r.name = "Draft"


class SaleCommissionMixin(models.AbstractModel):
    _inherit = "sale.commission.mixin"

    def _prepare_agent_vals(self, agent):
        return {
            "agent_id": agent.id,
            "commission_id": agent.commission_id.id,
            "commission_ids": agent.commission_ids.mapped("commission_id").ids,
        }

    def _prepare_agents_vals_partner(self, partner):
        # replaced OCA sale_commission sale_commission_mixin.py
        """Utility method for getting agents creation dictionary of a partner."""
        if not self.product_id:
            return False
        return [
            (0, 0, self._prepare_agent_vals(agent))
            for agent in partner.agent_line_ids.mapped("agent_id")
        ]


class CommissionItem(models.Model):
    _name = "commission.item"
    _description = "Commission Item"
    _order = "sequence, applied_on, categ_id desc, id desc"

    sequence = fields.Integer(default=10)
    commission_id = fields.Many2one("sale.commission")
    use_pricelist = fields.Boolean()
    pricelist_id = fields.Many2one("product.pricelist")
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
        [("sol", "Any Sale Order Line"), ("discount", "Discount")],
        string="Based On",
        required=True,
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

    @api.onchange("based_on")
    def onchange_based_on(self):
        if (
            not self.commission_id.use_discount_in_ct_lines
            and self.based_on == "discount"
        ):
            raise ValidationError(
                _("Please enable discount feature in the settings first.")
            )

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

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        if view_type == "tree":
            use_pricelist = (
                self.env["ir.default"].sudo().get("commission.item", "use_pricelist")
            )
            self = self.with_context(default_use_pricelist=use_pricelist)
        res = super(CommissionItem, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        return res
