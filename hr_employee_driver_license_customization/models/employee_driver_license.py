# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployeeDriverLicense(models.Model):
    _name = 'hr_employee_driver_license'
    _description = 'Employees drivers license'

    name = fields.Selection(
        string='Grade of drivers license',
        selection=[('first_grade', 'First grade'), ('second_grade', 'Second grade'), ('third_grade', 'Third grade'), 
        ('fourth_grade','Fourth grade'), ('fifth_grade', 'Fifth grade'), ('tsp', 'Higher Professional Degree (TSP)')]
    )

    
    type_of_drivers_license = fields.Selection(
        string='Type of drivers license',
        selection=[('type_a', 'Type A'), ('type_b', 'Type B')]
    )
    

    def name_get(self):
        msg = []
        for record in self:
            type_drivers_license = _('Type A') if record.type_of_drivers_license == 'type_a' else _('Type B')
            if record.name == 'first_grade':
                name = _('First grade') + ' - ' + type_drivers_license
            elif record.name == 'second_grade':
                name = _('Second grade') + ' - ' + type_drivers_license
            elif record.name == 'third_grade':
                name = _('Third grade')
            elif record.name == 'fourth_grade':
                name = _('Fourth grade')
            elif record.name == 'fifth_grade':
                name = _('Fifth grade')
            else:
                name = _('Higher Professional Degree (TSP)')
            msg.append((record.id, name))
            name = ' '
        return msg