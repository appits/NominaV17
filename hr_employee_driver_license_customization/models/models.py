# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    
    drive_license_ids = fields.Many2many(
        string='Employees drivers license',
        comodel_name='hr_employee_driver_license',
        ondelete='restrict',
    )
    