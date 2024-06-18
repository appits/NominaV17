# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployeeChildren(models.Model):
    _name = 'hr_employee_children'
    _description = 'Employee children'
    _order = 'birhtdate desc'

    
    name = fields.Char(
        string='Childs full name',)
    
    active = fields.Boolean(
        default=True, help="Set active to false to hide the children tag without removing it.")

    
    guardianship = fields.Boolean(
        string='Guardianship',
    )
    

    birhtdate = fields.Date(
        string='Birhtdate',)
    
    age = fields.Integer(
        string='Age',)
    
    type_age = fields.Selection(
        string='Type age',
        selection=[('months', 'Months'), ('years', 'Years')],
    )

    study_level = fields.Selection(
        string='Study level',
        selection=[('1', 'Elementary school'), ('2', 'High School'), ('3', 'University')]
    )

    child_has_ci = fields.Boolean(
        string='Child has ci',)

    child_ci = fields.Char(
        string='Child ci',)
    
    child_parent_ci = fields.Char(
        string='Child father ci',)

    child_mother_ci = fields.Char(
        string='Child mother ci',)

    employee_id = fields.Many2one(
        string='Parents',
        comodel_name='hr.employee',
        ondelete='restrict',
        store=True
    )
    
    @api.onchange('birhtdate')
    def _children_age(self):
        self.age = relativedelta(datetime.now(),self.birhtdate).years