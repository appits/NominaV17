# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployeeDisability(models.Model):
    _name = 'hr_employee_disability'
    _description = 'Employees disability'

    
    name = fields.Char(
        string='Disability',
    )