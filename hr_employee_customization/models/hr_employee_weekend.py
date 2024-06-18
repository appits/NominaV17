# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployeeWeeked(models.Model):
    _name = 'hr_employee_weekend'
    _description = 'Number of Saturdays and Sundays'
    _order = 'weekend_date desc'
    
    name = fields.Integer(string='Number of Saturdays and Sundays')
    active = fields.Boolean(
        default=True, help="Set active to false to hide the Saturday and Sunday number tag without removing it.")

    weekend_date = fields.Date(string='Date')
    description = fields.Char(string='Description')

    def name_get(self):
        result = []
        msg = ' '
        for record in self:
            if record.name and record.weekend_date:
                msg = str(record.name) + _(' / ') + str(record.weekend_date)
            elif not record.weekend_date:
                msg = str(record.name)
            result.append((record.id, msg))
            msg = ' '
        return result

    @api.constrains('name')
    def _check_name(self):
        if self.name < 0:
            raise ValidationError(
                _('The number of Saturdays and Sundays must not be less than zero'))
        else:
            pass
