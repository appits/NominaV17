# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    disability = fields.Boolean(string='Disability')

    type_disability_ids = fields.Many2many(
        string='Employees type disability',
        comodel_name='hr_employee_disability',
        ondelete='restrict',
    )