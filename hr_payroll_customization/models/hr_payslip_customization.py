# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
import calendar
from odoo.tools.safe_eval import safe_eval


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    # Field to validate loans for employees
    loans_paid = fields.Boolean(default=False)
    # Field to validate employee utilities
    profit_paid = fields.Boolean(default=False)
    # Field to validate employee Vacation advance and vacation discounts
    vac_paid = fields.Boolean(default=False)

    # Field to validate loans for employees
    cancel_loans_paid = fields.Boolean(default=False)
    # Field to validate employee utilities
    cancel_profit_paid = fields.Boolean(default=False)
    # Field to validate employee Vacation advance and vacation discounts
    cancel_vac_paid = fields.Boolean(default=False)

    salary_advance_ids = fields.Many2many(
        comodel_name='hr_employee_salary_advance',
        related='employee_id.salary_advance_ids',
        ondelete='restrict',
    )

    monday_number_id = fields.Many2one(
        comodel_name='hr_employee_monday_number',
        string='Monday number', ondelete='restrict')

    weekend_id = fields.Many2one(
        comodel_name='hr_employee_weekend',
        string='Weekend', ondelete='restrict')

    custom_currency_id = fields.Many2one(
        string='Custom Currency',
        comodel_name='res.currency',
        ondelete='restrict'
    )

    monday_numbers = fields.Float(
        string='Monday numbers',
        default=0,
        tracking=True,
    )

    saturdays_sunday_numbers = fields.Float(
        string='Number of Saturdays and Sundays',
        default=0,
        tracking=True,
    )

    rate_id = fields.Many2one('res.currency.rate', string='Rate')
    rate_amount = fields.Float(string="Rate amount")

    # Tracking fields
    date_from = fields.Date(tracking=True)
    date_to = fields.Date(tracking=True)
    number = fields.Char(tracking=True)
    contract_id = fields.Many2one(tracking=True)
    struct_id = fields.Many2one(tracking=True)
    name = fields.Char(tracking=True)

    biweekly_advance = fields.Boolean(string="Biweekly advance", default=False)


    @api.onchange('payslip_run_id')
    def _get_biweekly_advance(self):
        if self.payslip_run_id:
            self.biweekly_advance = self.payslip_run_id.biweekly_advance


    @api.constrains('biweekly_advance', 'date_from', 'date_to')
    def _constrain_biweekly_advance(self):
        for slip in self:
            beginning_month = date(slip.date_from.year, slip.date_from.month, 1)
            fortnight_month = date(slip.date_from.year, slip.date_from.month, 15)
            if slip.biweekly_advance and (slip.date_from != beginning_month or slip.date_to != fortnight_month):
                raise ValidationError(_("Para utilizar esta opción, el periodo elegido debe ser la primera quincena del mes."))


    @api.onchange('state')
    def _onchange_state_payslip(self):
        self.ensure_one()
        if self.state in ['done', 'paid']:
            for leave in self.leaves_all_days_ids:
                leave.payslip_state = 'done'


    @api.constrains('monday_numbers','saturdays_sunday_numbers')
    def _check_monday_numbers_and_saturdays_sunday_numbers(self):
        weekly_settlement = self.env.ref('hr_rule_category_customization.hr_payroll_structure_007', raise_if_not_found=False)
        monthly_settlement = self.env.ref('hr_rule_category_customization.hr_payroll_structure_013', raise_if_not_found=False)
        confidential_settlement = self.env.ref('hr_rule_category_customization.hr_payroll_structure_019', raise_if_not_found=False)


    @api.onchange('name','date_from','date_to')
    def _calculate_mondays_weekend(self):
        if self.name:
            days = self._get_monday_saturday_sunday_numbers()
            self.monday_numbers = days.get('monday_numbers')
            self.saturdays_sunday_numbers = days.get('saturdays_sunday_numbers')
    
    def _get_monday_saturday_sunday_numbers(self):

        payslip_start_of_period = date(
            self.date_from.year, self.date_from.month, self.date_from.day)
        payslip_end_of_period = date(
            self.date_to.year, self.date_to.month, self.date_to.day)

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


    @api.onchange('rate_id')
    def _rate_onchange(self):
        company_currency = self.env.company.currency_id
        if self.rate_id:
            self.rate_amount = self.rate_id.company_rate if self.rate_id.currency_id == company_currency else self.rate_id.inverse_company_rate
        else:
            self.rate_amount = 0

    currency_id = fields.Many2one(related='struct_id.currency_id')

    #currency_id = fields.Many2one(related='contract_id.fiscal_currency_id')

    # Net amount
    def update_fortnightly_advance(self):
        contract_obj = self.contract_id._get_current_contract(self.employee_id)
        beginning_month = date(self.date_from.year, self.date_from.month, 1)
        fortnight_month = date(self.date_from.year, self.date_from.month, 15)
        
        if self.state == 'paid' and (self.date_from == beginning_month and self.date_to == fortnight_month):
            payslip_obj = self
        else:
            payslip_obj = False
        contract_obj.update_net_amount(self.employee_id,payslip_obj)
        return True

    def action_send_payslip_by_email(self):
        mapped_reports = self._get_pdf_reports()
        generic_name = _("Payslip")
        template = self.env.ref('hr_payroll_customization.mail_template_new_payslip_custom', raise_if_not_found=False)

        for report, payslips in mapped_reports.items():
            for payslip in payslips:
                attachments_vals_list = []
                pdf_content, dummy = report.sudo()._render_qweb_pdf(payslip.id)
                if report.print_report_name:
                    pdf_name = safe_eval(report.print_report_name, {'object': payslip})
                else:
                    pdf_name = generic_name
                attachments_vals_list.append({
                    'name': pdf_name,
                    'type': 'binary',
                    'raw': pdf_content,
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })
                # Send email to employees
                if template:
                    data_id = self.env['ir.attachment'].sudo().create(attachments_vals_list)
                    template.attachment_ids = [(6, 0, [data_id.id])]
                    template.send_mail(payslip.id, notif_layout='mail.mail_notification_light', force_send=True)
                    template.attachment_ids = [(3, data_id.id)]

    def get_today(self):
        return fields.Date.today()

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        # Recalculo de conteos de dias fuera de contrato 
        res = super(HrPayslipInherit, self)._get_worked_day_lines(domain, check_out_of_contract)
        self._calculate_mondays_weekend()

        index = -1
        work_entry_id = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract').id
        for i, r in enumerate(res):
            if r['work_entry_type_id'] == work_entry_id:
                index = i
        if index == -1:
            return res

        out_res = res[index]
        contract = self.contract_id
        hours_per_day = contract.resource_calendar_id.hours_per_day
        delta_day = relativedelta(self.date_to, self.date_from).days

        precontract = {}
        postcontract = {}

        if self.date_from < contract.date_start:
            date = min(contract.date_start + relativedelta(days=-1), self.date_to)
            precontract = self._counter_in_period(self.date_from, date)
        
        if contract.date_end and contract.date_end < self.date_to:
            date = max(self.date_from, contract.date_end + relativedelta(days=1))
            postcontract = self._counter_in_period(date, self.date_to)

        self.saturdays_sunday_numbers -= postcontract.get('weekend', 0) + precontract.get('weekend', 0)  
        if self.saturdays_sunday_numbers < 0:
            self.saturdays_sunday_numbers = 0

        self.monday_numbers -= postcontract.get('mondays', 0) + precontract.get('mondays', 0)  
        if self.monday_numbers < 0:
            self.monday_numbers = 0

        out_days = postcontract.get('total', 0) + precontract.get('total', 0)
        if self.date_to == date and date.day == 31 and delta_day == 15 and postcontract:
            out_days -= 1
        out_hours = out_days * hours_per_day

        if out_days:
            out_res['number_of_days'] = out_days
            out_res['number_of_hours'] = out_hours
        else:
            res.pop(index)

        return res
    
    def _counter_in_period(self, date_start, date_end):
        count_weekend = 0
        count_mondays = 0
        count_general = 0

        current_day = date_start
        while current_day <= date_end:
            if current_day.weekday() in [0]:
                count_mondays += 1
            
            if current_day.weekday() in [5, 6]:
                count_weekend += 1
            
            count_general += 1
            current_day += timedelta(days=1)

        return {'total': count_general, 'mondays': count_mondays, 'weekend': count_weekend}


    def action_payslip_paid(self):
        for slip in self:
            contract_obj = slip.contract_id._get_current_contract(slip.employee_id)

            if slip.biweekly_advance:
                contract_obj.net_amount = slip.net_wage
                continue

            rule = slip.line_ids.filtered(lambda x: x.code == "ADVQ")
            if rule:
                contract_obj.net_amount = 0

        super(HrPayslipInherit, self).action_payslip_paid()
