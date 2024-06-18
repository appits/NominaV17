from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'
    _description = 'Salary Structure Type'

    # default_schedule_pay = fields.Selection(selection_add=[
    # ('second_fortnight', 'Second monthly fortnight'),
    # ('bi-monthly',)], tracking=True)

    type_selection = [  ("week", "Weekly"),
                        ("month","Monthly"),
                        ("bi", "Biweekly")]
    payroll_type = fields.Selection(string="Payroll type", selection=type_selection, default="bi")