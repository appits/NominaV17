from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeType(models.Model):
    _name = "hr.employee.type"
    _description = "Employee type"

    name = fields.Char(string='Name')