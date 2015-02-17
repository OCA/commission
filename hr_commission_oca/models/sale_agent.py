
from openerp import models, fields


class sale_agent(models.Model):
    _inherit = "sale.agent"

    employee_id = fields.Many2one(
        "hr.employee",
        help="Employee associated to agent, is necessary for set an employee "
             "to settle commissions in wage."
    )
