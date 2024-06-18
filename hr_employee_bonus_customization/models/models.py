# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    
    employee_spouse_ci= fields.Char(
        string='Spouse ci',
    )

    employee_spouse_age = fields.Integer(
        string='Employee spouse age',)

    # Employee Mother
    employee_mothers_name = fields.Char(
        string='Employees mother name',
    )
    
    employee_mothers_birthdate = fields.Date(
        string='Employee mother birthdate',)

    employee_mothers_ci = fields.Char(
        string='Employee mother ci',
    )

    employee_mothers_age = fields.Integer(
        string='Employee mother age',)

    employee_mothers_guardianship = fields.Boolean(
        string='Mothers guardianship',
    )

    # Employee Father
    employee_fathers_name = fields.Char(
        string='Employees father name',
    )
    
    employee_fathers_birthdate = fields.Date(
        string='Employee father birthdate',)

    employee_fathers_ci = fields.Char(
        string='Employee father ci',
    )

    employee_fathers_age = fields.Integer(
        string='Employee father age',)

    employee_fathers_guardianship = fields.Boolean(
        string='Fathers guardianship',
    )

    children_ids = fields.One2many(
        string='Children',
        comodel_name='hr_employee_children',
        inverse_name='employee_id',
    )

    bonus_line_ids = fields.One2many(
        string='bonus lines',
        comodel_name='hr_employee_bonus_line',
        inverse_name='employee_id',
    )

    @api.onchange('birthday', 'spouse_birthdate', 'employee_mothers_birthdate', 'employee_fathers_birthdate')
    def _employee_age(self):
        self.employee_age = relativedelta(datetime.now(),self.birthday).years
        self.employee_spouse_age = relativedelta(datetime.now(),self.spouse_birthdate).years
        self.employee_mothers_age = relativedelta(datetime.now(),self.employee_mothers_birthdate).years
        self.employee_fathers_age = relativedelta(datetime.now(),self.employee_fathers_birthdate).years