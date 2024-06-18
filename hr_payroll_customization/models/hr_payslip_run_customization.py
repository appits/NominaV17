# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
import calendar

class HrPayslipRunInherit(models.Model):
    _inherit = 'hr.payslip.run'

    def _compute_employee_soo_cestaticket_payslip_run(self):
        company_obj = self.env.company
        if company_obj:
            self.social_security_salary = company_obj.minimum_salary
            self.salary_basket_ticket = company_obj.salary_basket_ticket
        else:
            self.social_security_salary = 0
            self.salary_basket_ticket = 0
        self.compute_field_payslip_run = True

    compute_field_payslip_run = fields.Boolean(compute='_compute_employee_soo_cestaticket_payslip_run')
    social_security_salary = fields.Float(string='Salary Social Security SSO', store=True)
    salary_basket_ticket = fields.Float(string='Salary Basket Ticket', store=True)

    monday_number_id = fields.Many2one(
        comodel_name='hr_employee_monday_number',
        string='Monday number', ondelete='restrict')

    weekend_id = fields.Many2one(
        comodel_name='hr_employee_weekend',
        string='Weekend', ondelete='restrict')

    rate_id = fields.Many2one('res.currency.rate', string='Rate')

    rate_amount = fields.Float(string="Rate amount")

    group_account_id = fields.Boolean(string="Agrupar Cuentas")

    monday_numbers = fields.Float(
        string='Monday numbers',
        default=0,
    )

    saturdays_sunday_numbers = fields.Float(
        string='Number of Saturdays and Sundays',
        default=0,
    )

    biweekly_advance = fields.Boolean(string="Biweekly advance", default=False)


    @api.constrains('biweekly_advance', 'date_start', 'date_end')
    def _constrain_biweekly_advance(self):
        for slip in self:
            beginning_month = date(slip.date_start.year, slip.date_start.month, 1)
            fortnight_month = date(slip.date_start.year, slip.date_start.month, 15)
            if slip.biweekly_advance and (self.date_start != beginning_month or self.date_end != fortnight_month):
                raise ValidationError(_("Para utilizar esta opción, el periodo elegido debe ser la primera quincena del mes."))


    @api.onchange('rate_id')
    def _rate_onchange(self):
        company_currency = self.env.company.currency_id
        if self.rate_id:
            self.rate_amount = self.rate_id.company_rate if self.rate_id.currency_id == company_currency else self.rate_id.inverse_company_rate
        else:
            self.rate_amount = 0

    # Net amount
    def payslip_run_update_fortnightly_advance(self):

        for payslip in self.slip_ids:
            payslip.update_fortnightly_advance()
        return True

    @api.constrains('monday_numbers','saturdays_sunday_numbers')
    def _check_monday_saturday_sunday_numbers(self):
        is_zero = False
        for record in self:
            is_zero = (record.monday_numbers <= 0) or (record.saturdays_sunday_numbers <= 0)
        if is_zero:
            raise ValidationError(("El número de lunes y el número de sábados y domingos para la nómina: %s. debe ser mayor que cero." % self.name ))

    
    @api.onchange('name','date_start','date_end')
    def _onchange_name(self):
        if self.name:
            days = self._get_monday_saturday_sunday_numbers()
            self.monday_numbers = days.get('monday_numbers')
            self.saturdays_sunday_numbers = days.get('saturdays_sunday_numbers')

    def _get_monday_saturday_sunday_numbers(self):

        payslip_start_of_period = date(
            self.date_start.year, self.date_start.month, self.date_start.day)
        payslip_end_of_period = date(
            self.date_end.year, self.date_end.month, self.date_end.day)

        monday_numbers = 0
        saturday_sunday_numbers = 0

        if payslip_start_of_period.month == payslip_end_of_period.month:
            """
                The start and end of the payroll period are in the same month.
            """
            for dia in range(payslip_start_of_period.day, payslip_end_of_period.day + 1):
                if(datetime(payslip_start_of_period.year, payslip_start_of_period.month, dia).weekday() == 0):
                    monday_numbers += 1
                if(datetime(payslip_start_of_period.year, payslip_start_of_period.month, dia).weekday() in [5, 6]):
                    saturday_sunday_numbers += 1
        elif payslip_end_of_period.month > payslip_start_of_period.month:
            """
                The payroll start and end periods have different months.
            """

            day_month = calendar.monthrange(
                payslip_start_of_period.year, payslip_start_of_period.month)[1]

            for dia in range(payslip_start_of_period.day, day_month + 1):
                if(datetime(payslip_start_of_period.year, payslip_start_of_period.month, dia).weekday() == 0):
                    monday_numbers += 1
                if(datetime(payslip_start_of_period.year, payslip_start_of_period.month, dia).weekday() in [5, 6]):
                    saturday_sunday_numbers += 1

            for dia in range(1, payslip_end_of_period.day + 1):
                if(datetime(payslip_end_of_period.year, payslip_end_of_period.month, dia).weekday() == 0):
                    monday_numbers += 1
                if(datetime(payslip_end_of_period.year, payslip_end_of_period.month, dia).weekday() in [5, 6]):
                    saturday_sunday_numbers += 1

        return {'monday_numbers': monday_numbers, 'saturdays_sunday_numbers': saturday_sunday_numbers}
    

    def action_paid(self):
        super().action_paid()

        unpaid = self.slip_ids.filtered(lambda x: x.state != 'paid')
        for slip in unpaid:
            slip.action_payslip_paid()
