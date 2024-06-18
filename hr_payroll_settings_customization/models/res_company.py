# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Global settings fields for the payroll module
    minimum_salary = fields.Monetary(related='company_id.minimum_salary', string='Minimum salary', readonly=False)
    minimum_salary_currency = fields.Many2one('res.currency', related='company_id.minimum_salary_currency', readonly=False)

    holidays = fields.Integer(related='company_id.holidays',string='Holidays', readonly=False)
    bonus_vacation = fields.Integer(related='company_id.bonus_vacation',string='Vacation bonus days', readonly=False)    

    profit_days = fields.Integer(related='company_id.profit_days', string='Profit days', readonly=False)

    salary_basket_ticket = fields.Monetary(related='company_id.salary_basket_ticket', string='Salary Basket Ticket', readonly=False)
    basket_ticket_currency = fields.Many2one('res.currency', related='company_id.basket_ticket_currency', readonly=False)

    payslip_currency = fields.Many2one('res.currency', related='company_id.payslip_currency', string='Currency of the Salary Basket', readonly=False)

    @api.constrains('minimum_salary', 'holidays', 'profit_days', 'salary_basket_ticket')
    def _check_fields(self):
        flag = True if (self.minimum_salary < 0 or self.holidays < 0 or self.profit_days <
                        0 or self.salary_basket_ticket < 0) else False
        if flag:
            raise ValidationError(
                _("Global amounts. The amount entered must not be less than zero."))


class Company(models.Model):
    _inherit = 'res.company'

    minimum_salary = fields.Monetary(string='Minimum salary', default=0)
    minimum_salary_currency = fields.Many2one('res.currency')

    holidays = fields.Integer(string='Holidays', default=0)
    bonus_vacation = fields.Integer(string='Vacation bonus days', default=0)

    profit_days = fields.Integer(string='Profit days', default=0)

    salary_basket_ticket = fields.Monetary(string='Salary Basket Ticket', default=0)
    basket_ticket_currency = fields.Many2one('res.currency')

    payslip_currency = fields.Many2one('res.currency', string='Currency of the Salary Basket')