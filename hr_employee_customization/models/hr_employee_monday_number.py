# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployeeMondayNumber(models.Model):
    _name = 'hr_employee_monday_number'
    _description = 'Employee monday numbers'
    _order = 'monday_number_date desc'
    
    name = fields.Integer(string='Monday number')
    active = fields.Boolean(
        default=True, help="Set active to false to hide the monday number tag without removing it.")

    monday_number_date = fields.Date(string='Date')
    description = fields.Char(string='Description')

    def name_get(self):
        result = []
        msg = ' '
        for record in self:
            if record.name and record.monday_number_date:
                msg = str(record.name) + _(' / ') + str(record.monday_number_date)
            elif not record.monday_number_date:
                msg = str(record.name)
            result.append((record.id, msg))
            msg = ' '
        return result
    
    @api.constrains('name')
    def _check_name(self):
        if self.name < 0:
            raise ValidationError(_('Monday number must not be less than zero'))
        else:
            pass
    