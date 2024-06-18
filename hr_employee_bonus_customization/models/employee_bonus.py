# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployeeBonus(models.Model):
    _name = 'hr_employee_bonus'
    _description = 'Employee bonus'
    _order = "date desc, amount desc"

    name = fields.Selection(
        string='Type',
        selection=[('1', 'Toy voucher'), ('2', 'School voucher'),
                ('3', 'Sundry bonds')]
    )

    active = fields.Boolean(
        default=True, help="Set active to false to hide the children tag without removing it.")

    description = fields.Char(
        string='Description',
    )

    
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('draft', 'Draft'),('assigned', 'Assigned')
        ,('cancel', 'Cancel')],
        default='new'
    )    

    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id,
        ondelete='restrict',
    )

    amount = fields.Monetary(
        string='Amount',)

    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
    )

    minimum_age = fields.Integer(
        string='Minimum age',
    )

    
    type_minimum_age = fields.Selection(
        string='Type minimum age',
        selection=[('months', 'Months'), ('years', 'Years')],
    )

    maximum_age = fields.Integer(
        string='Maximum age',
    )

    type_maximum_age = fields.Selection(
        string='Type maximum age',
        selection=[('months', 'Months'), ('years', 'Years')],
    )

    study_level = fields.Selection(
        string='Study level',
        selection=[('1', 'Elementary school'),
                ('2', 'High School'), ('3', 'University')]
    )

    bonus_line_ids = fields.One2many(
        string='Bonus line',
        comodel_name='hr_employee_bonus_line',
        inverse_name='bonus_id',
    )


    def name_get(self):
        msj = []
        for record in self:
            if record.name == '1':
                name = _('Toy voucher') + ' - ' + str(record.date)
            elif record.name == '2':
                name = _('School voucher') + ' - ' + str(record.date)
            else:
                name = _('Sundry bonds') + ' - ' + str(record.date)
            msj.append((record.id, name))
            name = ' '
        return msj

    def _search_employees(self, is_schooll_voucher=False):
        employee_obj = self.env['hr.employee'].search([]).filtered(lambda x: x.active == True)
        employee_list = []
        bonus_lines = []
        if self.name in ['1', '2']:
            """
                look for employees whose children's age (if any) 
                is within the range of the minimum and maximum 
                bonus age.
            """
            children_list = []
            aux_minimum_age = self.minimum_age
            aux_maximum_age = self.maximum_age
            for employee in employee_obj.filtered(lambda x: x.children_ids):
                for child in employee.children_ids:
                    aux_child_age = child.age
                    
                    if child.type_age == 'years':
                        aux_child_age = child.age * 12
                    
                    if self.type_minimum_age == 'years':
                        aux_minimum_age = self.minimum_age * 12
                    
                    if self.type_maximum_age == 'years':
                        aux_maximum_age = self.maximum_age * 12

                    
                    if not is_schooll_voucher:
                        # Toy voucher
                        children_list.append(aux_child_age >= aux_minimum_age and aux_child_age <= aux_maximum_age)
                    else:
                        # School voucher
                        children_list.append(aux_child_age >= aux_minimum_age and aux_child_age <= aux_maximum_age and child.study_level == self.study_level)
                if any(children_list):
                    bonus_lines.append({
                        'bonus_id': self.id,
                        'employee_id': employee.id,
                        'employee_bonus_amount': len(children_list) * self.amount,
                    })
                    employee_list.append(employee.id)
                children_list.clear()
        elif self.name == '3':
            # Sundry bonds
            for employee in employee_obj:
                bonus_lines.append({
                        'bonus_id': self.id,
                        'employee_id': employee.id,
                        'employee_bonus_amount': self.amount,
                    })
            employee_list = employee_obj.mapped('id')

        """
            Employees whose children's age (if any) 
            is within the minimum and maximum bonus age range.
        """
        if employee_list:
            self.env['hr_employee_bonus_line'].create(bonus_lines)
            self.write({"state": 'draft'})
        else:
            pass

    def search_employees(self):
        #TODO: Clear the entered information if you have changed the type of voucher, which was entered the first time.
        if self.name == '1':
            # Toy voucher
            self._search_employees()
        elif self.name == '2':
            # School voucher
            self._search_employees(True)
        elif self.name == '3':
            # Sundry bonds
            self._search_employees()

    def action_confirm(self):
        self.search_employees()
        self.write({"state": 'assigned'})

    def action_cancel(self):
        self.write({"state": 'cancel'})
    
    def action_draft(self):
        self.write({"state": 'draft'})


class HrEmployeeBonusLine(models.Model):
    _name = 'hr_employee_bonus_line'
    _description = 'Employee bonus line'
    _order = 'bonus_id desc'
    
    name = fields.Selection(
        related='bonus_id.name'
    )
    
    active = fields.Boolean(
        default=True, help="Set active to false to hide the children tag without removing it.")

    bonus_id = fields.Many2one(
        string='Bonus',
        comodel_name='hr_employee_bonus',
        ondelete='restrict',
    )

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        ondelete='restrict',
    )
    
    employee_bonus_amount = fields.Float(
        string='Employee bonus amount',
        
    )
