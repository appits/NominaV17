# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from calendar import monthrange
import logging

_logger = logging.getLogger(__name__)

class HrContractCustomization(models.Model):
    _inherit = 'hr.contract'

    #TODO: REFACTOR: base
    def _get_fiscal_currency(self):
        return self.env.user.company_id.currency_id
    
    def _get_today(self):
        return fields.Date.from_string(fields.Date.today())

    description_end_contract = fields.Many2one("hr.departure.reason", string='Motivo Egreso')

    custom_salary = fields.Monetary(string="Salary in $")
    custom_salary_currency = fields.Many2one('res.currency')
    
    department_name = fields.Char(related='department_id.name')

    net_amount = fields.Monetary(string='Biweekly advance')

    is_benefit_calculation_valid = fields.Boolean(string='Is day')
    
    #Details Fields
    employee_seniority = fields.Char(help="Employee Seniority")
    employee_years_seniority = fields.Float(
        help="Years of seniority of the employee")
    employee_months_seniority = fields.Float(
        help="Months of seniority of the employee")
    employee_days_seniority = fields.Float(
        help="Days of seniority of the employee")
    #//

    #Salary Fields
    wage_currency = fields.Many2one('res.currency', related='fiscal_currency_id', readonly=True) ##<-
    hourly_wage_currency = fields.Many2one('res.currency')

    fiscal_currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True, tracking=True) ##<-
    
    salary_assignment = fields.Monetary(string='Salary assignment')
    salary_assignment_currency = fields.Many2one('res.currency')

    average_salary = fields.Monetary(string='Average salary', default=0)
    average_salary_currency = fields.Many2one('res.currency')
    average_salary_date_start = fields.Date(
        string='Date start', help='Starting date from which the payrolls that are in paid status will be searched for the calculation of the average salary.')
    average_salary_date_end = fields.Date(
        string='Date end', help='End date up to which the payrolls that are in paid status will be searched for the calculation of the average salary.')

    overtime_hours = fields.Boolean( string='Overtime horus' )
    overtime_hours_amount = fields.Monetary( string='Overtime horus amount', default=0)
    overtime_hours_currency = fields.Many2one('res.currency')

    check_compute_security_salary = fields.Boolean(string='Actualizar Salario', default=True)

    compute_field_soo = fields.Boolean(
        compute='_compute_employee_soo_cestaticket')

    social_security_salary = fields.Monetary(string='Salary Social Security',
                                                default=lambda self: self.env.company.minimum_salary )
    
    social_security_currency = fields.Many2one('res.currency',
                                                    default=lambda self: self.env.company.minimum_salary_currency )
    
    salary_basket_ticket = fields.Monetary(string='Salary Basket Ticket',
                                                default=lambda self: self.env.company.salary_basket_ticket )
    
    basket_ticket_currency = fields.Many2one('res.currency',
                                                default=lambda self: self.env.company.basket_ticket_currency )

    #Withholdings Fields
    social_security = fields.Boolean(string='social Security')
    forced_unemployment = fields.Boolean(string="Forced unemployment")
    husing_policy_law = fields.Boolean(string="Housing policy law")
    withholding_discount_rate = fields.Float( digits=(2, 2),
        string="Withholding discount rate")    
    #//

    #Loans and salary advances
    compute_field_income_discounts = fields.Boolean( compute='_compute_employee')
    employee_loans = fields.Monetary(string='Salary advances', default=0)
    employee_dpres = fields.Monetary(
        string='Salary advance discounts',
        compute='_compute_employee_dpres',
        store=True)


    next_cuota = fields.Monetary(
        string='Proxima Cuota',
        compute='_compute_employee_next_cuota',
        store=True)

    employee_result_loans = fields.Monetary(string='Total loans', default=0)
    
    salary_advance_ids = fields.Many2many(comodel_name='hr_employee_salary_advance', related="employee_id.salary_advance_ids")

    # #Profits
    profit_days = fields.Integer(string='Profit days', related="company_id.profit_days")

    profit_factor = fields.Float(string="Profit factor", compute="_compute_profit_factor")

    profit_msg = fields.Boolean(default=False, help="Active profit message of invalid input")
    profit_accrued = fields.Monetary(string="Accrued profit")
    profit_accrued_date = fields.Date(string="Accrued profit date", default=_get_today)

    profit_accumulated = fields.Monetary(string="Profit accumulated", compute="_get_profit_accrued_accumulated")
    profit_add = fields.Monetary(string="Accumulated profits",
                                        help="Set a base amount to the accomulated profit")
    profit_add_date = fields.Date(string="Accumulated profits date")

    profit_advance = fields.Monetary(string="Profit advances", compute="_advance_profit")

    profit_paid = fields.Monetary(string="Profits paid", default=0)

    profit_total = fields.Monetary(string="Profits total", compute="_get_profit_total")

    # #Advance vacation
    employee_holiday_advance = fields.Monetary(
        string='Advance vacation', compute="_vaction_advances_calculation")
    employee_holiday_depresvac_amount = fields.Monetary(
        string='Vacation Advance Discounts', default=0)
    employee_total_holiday_advance = fields.Monetary(
        string='Total holiday advance', default=0)

    # #Vacation bonus counter
    employee_vacation_bonus = fields.Monetary(string='Vacation bonus', default=0)
    #//
    
    #Incomes and Discounts additionals Fields
    employee_fixed_additional_income_discounts_ids = fields.One2many(
        comodel_name='hr_employee_additional_discount_income',
        inverse_name='contract_id', compute='_compute_employee', string='Fixed additional income')
    #//

    #Social Benefits
    quarterly_payment = fields.Date(string="Quarterly payment", default=_get_today, readonly=False, compute="_set_quarterly_payment_today")

    accrued_benefits = fields.Monetary(   string="Accumulated benefits", default=0,
                                                help="Set a base amount to the garantee social benefits")
    accrued_benefits_date = fields.Date( string='Date of accrued benefits')

    guarantee_days = fields.Integer(compute="_guarantee_social_benefits", help="Guarantee of social benefits days")
    guarantee_salary = fields.Monetary(help="Guarantee of social benefits salary")
    guarantee_msg = fields.Boolean(default=False, help="Active guarantee of social benefits salary message of invalid input")

    add_accrued = fields.Monetary(   string="Accumulated additional days", default=0,
                                                help="Set a base amount to the additional days social benefits")
    add_accrued_date = fields.Date( string='Date of additional days')

    additional_days = fields.Integer(compute="_additional_social_benefits", help="Additional days of social benefits")
    additional_salary = fields.Monetary(help="Additional days of social benefits salary")
    additional_sum = fields.Boolean(string="Acomulate additional days",
                                    default=False, help="When this is active, the amount of additional days of social benefits is going to be acumulated")
    
    advance_social_benefits = fields.Monetary(string="Social benfits advances", compute="_advance_social_benefits")
    advance_social_benefits_extra = fields.Monetary(string="Previous social benfits advances", default=0,
                                                    help="Set a base amount to the advances of social benefits")

    available_social_benefits = fields.Monetary(string='Total available social benefits', compute="_available_social_benefits", default=0)

    interest_social_benefits_aux = fields.Monetary(default=0)    
    interest_social_benefits_add = fields.Monetary(string="Previous interest on social benefits", default=0,
                                                help="Set a base amount to the interest on social benefits")    
    interest_social_benefits = fields.Monetary(string="Interest on social benefits", default=0)
    interest_sum = fields.Boolean(string="Acomulate interest",
                                    default=False, help="When this is active, the amount of interest on social benefits is going to be acumulated")

    trust_contribution = fields.Monetary(string="Trust Contribution", default=0)
    trust_condition = fields.Selection(related="company_id.trust_config")

    payroll_rate_id = fields.Many2one(  "hr.payroll.rate", string="Actual rate of social benefits", compute="_get_lastes_rate",
                                        help="""
                                            This fields are the lastest date and rate to apply to social benefits' calculation.
                                            This have to be rate approved to Central Bank of Venezuela.    
                                        """)
    payroll_rate = fields.Float(related="payroll_rate_id.rate")
    #//

    #social benefits methods
    def _set_quarterly_payment_today(self):
        for record in self:
            record.quarterly_payment = record._get_today()

    @api.depends("quarterly_payment", "accrued_benefits_date", "state")
    def _guarantee_social_benefits(self):
        for contract in self:
            contract._set_trust_contribution_salary(contract.trust_condition )

            if contract.state == "cancel":
                contract.guarantee_days = 0
                contract.guarantee_salary = 0
                return

            contract.guarantee_msg = False

            current_contract = contract._get_current_contract(contract.employee_id)
            if current_contract:
                seniority = current_contract._get_employee_seniority(contract.quarterly_payment, True)

                if seniority['today'] < contract.quarterly_payment or contract.quarterly_payment < contract.date_start:
                    contract.guarantee_days = 0
                    contract.guarantee_salary = 0
                    contract.guarantee_msg = True
                    return

                total_month = seniority['months'] + (seniority['years'] * 12)
                quarterly = total_month // 3
                total_count = 15 * quarterly

                contract.guarantee_days = total_count
                contract.guarantee_salary = contract._amount_social_benefits(quarterly)
                
                #if there's old amount from external sources, can add it to this total
                limit_date = contract.accrued_benefits_date
                if limit_date:
                    if limit_date >= contract.quarterly_payment:
                        contract.guarantee_salary = 0
                    else:
                        contract.guarantee_salary += contract.accrued_benefits
            
            else:
                contract.guarantee_days = 0
                contract.guarantee_salary = 0


    def _amount_social_benefits(self, count):
        #-- (integral salary / 30) * 15 --#
        res = 0
        for i in range(1, count+1):
            integral_salary = self._integral_salary_social_benefits(3*i)
            res += integral_salary * 15

        return res
    
    @api.depends("quarterly_payment", "additional_sum", "add_accrued_date", "state")
    def _additional_social_benefits(self):
        for contract in self:
            if contract.state == "cancel":
                contract.additional_days = 0
                contract.additional_salary = 0
                return

            current_contract = self._get_current_contract(contract.employee_id)
            if current_contract:
                seniority = current_contract._get_employee_seniority(contract.quarterly_payment, True)

                if seniority['today'] < contract.quarterly_payment or contract.quarterly_payment < contract.date_start:
                        contract.additional_days = 0
                        contract.additional_salary = 0
                        return

                if seniority['years'] >= 16:
                    total_count = 30
                elif seniority['years'] >= 2:
                    total_count = (seniority['years'] - 1) * 2
                else:
                    total_count = 0

                contract.additional_days = total_count
                contract.additional_salary = contract._amount_additional_social_benefits(seniority['years'])

                limit_date = contract.add_accrued_date
                if limit_date:
                    if limit_date >= contract.quarterly_payment:
                        contract.additional_salary = 0
                    else:
                        contract.additional_salary += contract.add_accrued
            
            else:
                contract.additional_days = 0
                contract.additional_salary = 0 

    
    def _amount_additional_social_benefits(self, count):
        #-- (integral salary / 30) * additional_days --#
        res = 0

        if count >= 2:
            for i in range(2, count+1):
                integral_salary = self._integral_salary_social_benefits(-1, i)
                days = 2 * (i - 1)
                days = 30 if days > 30 else days
                add = integral_salary * days

                if not self.additional_sum:
                    date = self.date_start + relativedelta(years=+i)
                    rest = self._paid_interest(date, ["DIAPPSS"])
                else:
                    rest = 0

                res += add - rest

        return res

    def _integral_salary_social_benefits(self, count, count_year=0):
        #-- [(aliquot_vacation * daily_salary) + (aliquot_utility * daily_salary)] + daily_salary --#
        normal_daily_salary = self._get_normal_daily_salary(count, count_year)
        aliquot_vacation = self._get_aliquot_vacation()
        aliquot_utility = self._get_aliquot_utility()

        integral_salary = ((aliquot_vacation * normal_daily_salary) + (aliquot_utility * normal_daily_salary)) + normal_daily_salary

        return integral_salary

    def _get_normal_daily_salary(self, days, years=0):
        daily_salary = 0
        today = fields.Date.from_string(fields.Date.today())
        
        date = self.date_start + relativedelta(months=+days, years=+years)
        
        date_ini = date.replace(day=1)
        lasday = monthrange(date.year, date.month)[1]
        date_end = date.replace(day=lasday)

        if self.structure_type_id.payroll_type == 'week':
            date_ini, date_end = self._weekly_period(date_ini, date_end)
            payroll_type = 28 

        else:
            payroll_type = 30

        values = self._get_values_accrued([(date_ini, date_end)])
        accrued = self._convert_to_fiscal(values)
        #TODO: discount DED category (check it) 
        # ded = self._paid_interest(date_ini, ["DED"], True)
        # accrued -= ded

        if accrued < self.wage:
            accrued = self.wage
            payroll_type = 30

        daily_salary = accrued / payroll_type
        if self.accrued_benefits_date and date_ini < self.accrued_benefits_date and years == 0:
            daily_salary = 0

        if self.add_accrued_date and date_ini < self.add_accrued_date and years != 0:
            daily_salary = 0

        return daily_salary

    def _get_values_accrued(self, dates):
        """Return a list of dictionaries that contains:
            'currency_id': id of the currency used in the payslip
            'total': accrued amount using this specific currency during specified period

            :param dates: a list of tuples that have all periods to do the query
        """

        if not dates:
            return None
        
        where_date = ""
        for date in dates:
            where_date += " ('{0}' <= payslip.date_from AND payslip.date_to <= '{1}') OR".format(*date)

        query = """
            SELECT
                DISTINCT(struct_type.currency_id),
                COALESCE(SUM(line.amount), 0) AS total
            FROM hr_payslip_line AS line 
                JOIN hr_payslip AS payslip ON line.slip_id = payslip.id
                JOIN hr_salary_rule_category AS categ ON line.category_id = categ.id
                JOIN hr_payroll_structure AS struct ON payslip.struct_id = struct.id
                JOIN hr_payroll_structure_type AS struct_type ON struct.type_id = struct_type.id
            WHERE
                payslip.employee_id = {id}
                AND payslip.state = 'paid'
                AND categ.code IN ('BASIC', 'BASIC2', 'BASIC3')
                AND {condition}
            GROUP BY
                struct_type.currency_id

        """.format(id = self.employee_id.id, condition = where_date[:-2])

        self._cr.execute(query)
        data = self.env.cr.dictfetchall()
        return data

    def _get_aliquot_vacation(self):
        return self.env.company.bonus_vacation / 360

    def _get_aliquot_utility(self):
        return self.env.company.profit_days / 360
    
    @api.depends('salary_advance_ids', 'advance_social_benefits_extra', 'quarterly_payment')
    def _advance_social_benefits(self):
        for contract in self:
            list_advance = contract.salary_advance_ids.filtered(lambda x: 
                                                                x.reason == '1' \
                                                                and x.state == "approved"\
                                                                and x.date <= contract.quarterly_payment)

            total = 0
            for advance in list_advance:
                currency = contract.fiscal_currency_id
                date = advance.rate_id.name or fields.Date.today()

                if advance.currency_id != currency and not advance.rate_id:
                    total += currency._convert_payroll(advance.advancement, advance.currency_id, contract.company_id, date)
                else:
                    total += advance.currency_id._convert_payroll(advance.advancement, currency, contract.company_id, date)

            contract.advance_social_benefits = total
            contract.advance_social_benefits += contract.advance_social_benefits_extra
            
    
    @api.depends("guarantee_salary", "advance_social_benefits", "additional_days")
    def _available_social_benefits(self):
        for contract in self:
            available = (contract.additional_salary + contract.guarantee_salary) - contract.advance_social_benefits
            available = 0 if available < 0 else available

            contract.available_social_benefits = available

    @api.constrains('interest_social_benefits_add')
    def constrains_interest_add(self) -> None:
        """ Add previous amount of interest """
        self.interest_social_benefits -= self.interest_social_benefits_aux
        if self.interest_social_benefits < 0:
            self.interest_social_benefits = 0
        self.interest_social_benefits += self.interest_social_benefits_add

        self.interest_social_benefits_aux = self.interest_social_benefits_add


    def calculation_interest_social_benefits(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open')])
        for contract in contracts:
            contract._interest_social_benefits()


    def _interest_social_benefits(self):
        #-- (aviable social benefits * (rateBCV / 100) / 360) * 30 --#
        if self.state == "cancel":
            self.interest_social_benefits = 0
            return

        self.update_social_benefit()

        rate = self.payroll_rate / 100
        social_benefits = (self.available_social_benefits * rate) / 360
        total = social_benefits * 30

        if self.interest_sum:
            self.interest_social_benefits += total
        else:
            today = self._get_today() + relativedelta(months=-1)

            value = 0 if self._paid_interest(today, ["INTEREST"]) else total
            #validar cuando sumar o asignar con interest_add 
            if  self.interest_social_benefits_add and \
                ((value == total and total == 0) or (value > 0)) :
                self.interest_social_benefits = value + self.interest_social_benefits_add
            else:
                self.interest_social_benefits = value
                if value == 0: self.interest_social_benefits_add = 0


    def _get_lastes_rate(self):
        self.payroll_rate_id = self.payroll_rate_id._get_lastest_rate()

    def update_social_benefit(self):
        self.quarterly_payment = self._get_today()
        self._guarantee_social_benefits()
        self._advance_social_benefits()
        self._advance_social_benefits()
        self._get_lastes_rate()


    def _weekly_period(self, date_ini, date_end, date=None):
        """
            receives initial date and end date from a period
            if the contract is associated with a weekly payroll, adjusts the period for complete every week in the month

            :return:
                date_ini and date_end modified
        """
        
        if self.structure_type_id.payroll_type == 'week':
            if date:
                date -= timedelta(7)
                start_of_week = date - timedelta(days=date.weekday())

                date_ini = start_of_week - timedelta(21)
                date_end = start_of_week + timedelta(days=6)

            else:
                day_ini = date_ini.weekday()
                if day_ini <= 3: #is thursday
                    date_ini = date_ini + relativedelta(days=-day_ini)

                day_end = date_end.weekday()
                if day_end >= 3: #is thursday
                    plus = 7 - (day_end + 1)
                    date_end = date_end + relativedelta(days=+plus)

        return date_ini, date_end


    def _paid_interest(self, date, codes, categ=False, limit=True):
        """
            This function can find the amount of salary rules or a complete category
            in a month that have the codes brang by parameter 'codes'

            :param:
                date: date with the month to search values of rules or categories
                codes: a list of codes (must be string type)
                categ: a flag. If is true, the codes are for categories. Otherwise the codes are for rules

            :result:
                (float) the total amount of all codes converted to the fiscal currency
        """

        data = []
        if self.employee_id.id:
            date_ini = date.replace(day=1)
            lasday = monthrange(date.year, date.month)[1]
            date_end = date.replace(day=lasday)
            stand, date_end = self._weekly_period(date_ini, date_end)

            codes = "', '".join(codes)
            if not categ:
                condition = "AND line.code IN ('{codes}')".format(codes=codes)            
            else:
                condition = "AND categ.code IN ('{codes}')".format(codes=codes)

            if limit:
                l = "date_to" 
                date_ini = stand
            else:
                l = "date_from"

            query = """
                SELECT
                    DISTINCT(struct_type.currency_id),
                    COALESCE(SUM(line.total), 0) AS total
                FROM hr_payslip_line AS line 
                    JOIN hr_payslip AS payslip ON line.slip_id = payslip.id
                    JOIN hr_salary_rule_category AS categ ON line.category_id = categ.id
                    JOIN hr_payroll_structure AS struct ON payslip.struct_id = struct.id
                    JOIN hr_payroll_structure_type AS struct_type ON struct.type_id = struct_type.id
                WHERE
                    payslip.employee_id = {id}
                    {condition}
                    AND payslip.state in ('done', 'paid')
                    AND '{ini}' <= payslip.date_from AND payslip.{limit} <= '{end}'
                GROUP BY
                    struct_type.currency_id
            """.format(id=self.employee_id.id, condition=condition, ini=date_ini, end=date_end, limit=l)
            self._cr.execute(query)
            data = self.env.cr.dictfetchall()
        
        return self._convert_to_fiscal(data)


    def _convert_to_fiscal(self, data):
        today = self._get_today()
        accrued = 0
        for value in data:
            if value['currency_id'] == self.fiscal_currency_id.id:
                aux = value['total']
            else:
                currency = self.env['res.currency'].search([('id', '=', value['currency_id'])])
                aux = currency._convert_payroll(value['total'], self.fiscal_currency_id, self.company_id, today)

            accrued += aux

        return accrued


    def _selected_available_social_benefits(self, date):
        self.quarterly_payment = date
        self._guarantee_social_benefits()
        self._additional_social_benefits()
        self._advance_social_benefits()

        available = (self.additional_salary + self.guarantee_salary) - self.advance_social_benefits
        available = 0 if available < 0 else available

        return available


    def _set_trust_contribution_salary(self, trust_config):
        if trust_config == 'ing':
            current_contract = self._get_current_contract(self.employee_id)
            if self != current_contract:
                self.trust_contribution = 0
                return

            seniority = self._get_employee_seniority()
            total_month = seniority['months'] + (seniority['years'] * 12)
            quarterly = total_month / 3

            today = self._get_today()
            paid = self._paid_interest(today, ["AFID"])

            if quarterly.is_integer():
                integral_salary = self._integral_salary_social_benefits(quarterly * 3)
                self.trust_contribution = integral_salary * 15 if not paid else 0

            if paid:
                self.trust_contribution = 0

        elif trust_config == 'no':
                self.trust_contribution = 0


    def _trust_contribution_salary(self):
        try:
            today = self._get_today()
            limit = today.replace(day=1) - relativedelta(months=3)
            de = today.replace(day=1) - relativedelta(days=1)
            di = de.replace(day=1)

            contracts = self.search([('state', '=', 'open')])
            for c in contracts:
                if limit <= c.date_start <= de:
                    c.trust_contribution = 0
                    continue

                c.trust_contribution = 15 * c._get_trust_salary(di, de, today)

            _logger.warning("trust contribution cron successfuly!")
        except:
            _logger.warning("ERROR: error in trust contribution cron!")


    def _get_trust_salary(self, di, de, today):
        di, de = self._weekly_period(di, de, today)

        data = self._get_values_accrued([(di, de)])
        accrued = self._convert_to_fiscal(data)
        payroll_type = 28 if self.structure_type_id.payroll_type == 'week' else 30
        if accrued < self.wage:
            accrued = self.wage
            payroll_type = 30
        daily_salary = accrued / payroll_type

        aliquot_vacation = self._get_aliquot_vacation()
        aliquot_utility = self._get_aliquot_utility()

        integral_salary = ((aliquot_vacation * daily_salary) + (aliquot_utility * daily_salary)) + daily_salary
        return integral_salary
    #//


    #//Base
    # Return the current contract of the employee
    def _get_current_contract(self, employee):
        # Active contract(s) of the employee
        if employee:
            actives_contracts = employee._get_first_contracts()
            
            date_current_contract = max(actives_contracts.mapped( 'date_start')) if actives_contracts else False
            current_contract = actives_contracts.filtered( lambda c: c.date_start == date_current_contract)
            
            if len(current_contract) > 1:
                current_contract = current_contract[0]
        
        else:
            current_contract = False
            
        return current_contract

    # Returns the months and years of seniority of the employee
    def _get_employee_seniority(current_contract, is_today=None, legal=False):
        today = fields.Date.from_string(fields.Date.today())
        date = current_contract.date_start

        limit_date = datetime(1997, 6, 19).date()
        if legal and limit_date >= date:
            date = limit_date

        if is_today:
            seniority = relativedelta(is_today, date)
        elif not current_contract.date_end:
            seniority = relativedelta(today, date)
        else:
            seniority = relativedelta(current_contract.date_end, date)

        return {'today': today, 'days': seniority.days, 'months': seniority.months, 'years': seniority.years}
    
    #TODO: probar con un related al campo 'employee_additional_discounts_ids'
    def _compute_employee(self):
        if self.employee_id.employee_additional_discounts_ids:
            # Additional Income
            self.write({'employee_fixed_additional_income_discounts_ids': [
                    (6, 0, self.employee_id.employee_additional_discounts_ids.ids)]})
        else:
            self.employee_fixed_additional_income_discounts_ids = False

        self.compute_field_income_discounts = True

    def _compute_employee_soo_cestaticket(self):
        self.compute_field_soo = True
    
    def _compute_net_amount(self, payslip_obj, to_currency, average_salary=False):
        payroll = 0
        discount = 0

        if payslip_obj:
            for payslip in payslip_obj:
                currency_id = payslip.currency_id if not average_salary else self.average_salary_currency
                
                payroll += sum(currency_id._convert_payroll(total.total, to_currency, payslip.company_id, payslip.rate_id.name or fields.Date.today()) for total in payslip.line_ids.filtered(lambda x: x.category_id.code in [
                    'BASIC', 'BASIC2', 'BASIC3']))
                
                discount += sum(currency_id._convert_payroll(total.total, to_currency, payslip.company_id, payslip.rate_id.name or fields.Date.today()) for total in payslip.line_ids.filtered(lambda x: x.category_id.code in [
                    'DED']))
                
        return payroll - discount

    # Average salary
    @api.onchange('wage','average_salary_date_start', 'average_salary_date_end')
    def _onchange_average_salary(self):
        """
            step 1: Search for payrolls in paid status that are in the range of 
            average_salary_date_start and average_salary_date_end.
        """
        payslip_obj = self.env['hr.payslip'].search(
            [('employee_id', '=', self.employee_id.id), ('state', 'in', ['done', 'paid']), ('date_from', '>=', self.average_salary_date_start), ('date_to', '<=', self.average_salary_date_end)])
        
        """
            step 2: calculate the net of the sum of the lines in the wage calculation 
            of the payroll whose code is in : Basic, Basic2, Basic3
        """


        neto = self._compute_net_amount(payslip_obj, self.average_salary_currency, True)
        
        # Segun ley si eñ neto es menor que el salario entre 30 se deja el calculo del salario
        
        if neto < (self.wage):
            neto = self.wage 

        """
            step 3: calculate the number of weeks between the range of 
            average_salary_date_start and average_salary_date_end
        """
        # anteriormente se calculaba el numero de semanas, pero segun el funcional siempre debe ser a 30 dias asi que no es importante calcular los dias
        if self.average_salary_date_start and self.average_salary_date_end:
        
            self.average_salary = (neto / 30 )  if neto > 0 else 0


    @api.onchange('check_compute_security_salary')
    def onchange_check_compute_security_salary(self):
        for record in self:
            if record.check_compute_security_salary:
                # Realizar el cálculo aquí                          
                record.social_security_salary =  record.env.company.minimum_salary
                record.social_security_currency = record.env.company.minimum_salary_currency
                record.salary_basket_ticket = record.env.company.salary_basket_ticket
                record.basket_ticket_currency = record.env.company.basket_ticket_currency
    #//

    #// Profits
    # Utilities and Advances of utilities
    def _compute_profit_factor(self):
        self.profit_factor = self._get_aliquot_utility()


    @api.onchange('profit_accrued_date')
    def _get_profit_accrued(self):
        date = self.profit_accrued_date
        total = 0
        if date:
            basic = self._paid_interest(date, ["BASIC", "BASIC2", "BASIC3", "UTIL"], True, limit=False)
            ded = self._paid_interest(date, ["DED", "DED2"], True, limit=False)

            total += basic - ded

        self.profit_accrued = total


    @api.onchange('profit_add', 'profit_add_date')
    def _get_profit_accrued_accumulated(self):
        today = self._get_today()
        for c in self:
            flag = False
            try:    
                if c.profit_add_date > c.date_end:
                    flag = True
            except: pass

            if c.profit_add_date and (today < c.profit_add_date or c.profit_add_date < c.date_start  or flag):
                c.profit_msg = True
                c.profit_accumulated = 0 
                return
            c.profit_msg = False
            
            date = (c.profit_add_date or c.date_start).replace(day=2)
            after_date = date + relativedelta(months=+1)
            current = today.replace(day=1)

            total = c.profit_add if c.profit_add_date else 0
            clean = 0
            while date <= current:
                basic = c._paid_interest(date, ["BASIC", "BASIC2", "UTIL"], True, limit=False)
                ded = c._paid_interest(date, ["DED"], True, limit=False)

                total += basic - ded

                clean = c._paid_interest(after_date, ["UTILIDADESD"], limit=False)
                total = 0 if clean > 0 else total

                date = after_date
                after_date = date + relativedelta(months=+1)

            c.profit_accumulated = 0 if clean > 0 else total
            c._get_profit_paid(clean)


    @api.depends("advance_social_benefits")
    def _advance_profit(self):
        for contract in self:
            list_advance = contract.salary_advance_ids.filtered(lambda x: x.reason == '2' and x.state == "approved")

            total = 0
            for advance in list_advance:
                currency = contract.fiscal_currency_id
                date = advance.rate_id.name or fields.Date.today()

                if advance.currency_id != currency and not advance.rate_id:
                    total += currency._convert_payroll(advance.advancement, advance.currency_id, contract.company_id, date)
                else:
                    total += advance.currency_id._convert_payroll(advance.advancement, currency, contract.company_id, date)

            contract.profit_advance = total


    def _get_profit_paid(self, util_def):
        self.profit_paid = self.profit_paid if not util_def else 0


    def _get_profit_total(self):
        self.profit_total = self.profit_factor * self.profit_accumulated
    #//

    #// Loans and salary advances
    # Vacation advance and vacation discounts
    def _compute_employee_holiday_advance(self, payslip_obj, contract_obj):
        # Advance vacation
        advancement_bs = sum(line.currency_id._convert_payroll(line.advancement, self._get_fiscal_currency(), contract_obj.company_id, line.rate_id.name or fields.Date.today(
        )) for line in contract_obj.salary_advance_ids.filtered(lambda x: x.reason == '4' and not x.advance_vacation and x.state in ['approved']))
        contract_obj.employee_holiday_advance = advancement_bs

        # Vacation bonus counter
        advancement_bs = sum(line.currency_id._convert_payroll(line.advancement, self._get_fiscal_currency(), contract_obj.company_id, line.rate_id.name or fields.Date.today(
        )) for line in contract_obj.salary_advance_ids.filtered(lambda x: x.reason == '4' and x.advance_vacation and x.state in ['approved']))
        contract_obj.employee_holiday_advance = advancement_bs

        # DEPRESVAC
        if payslip_obj:
            for payslip in payslip_obj:
                paid = False
                for line in payslip.line_ids.filtered(lambda x: x.code in ['DEPRESVAC']):
                    paid = True
                    if not payslip.vac_paid:
                        contract_obj.employee_holiday_depresvac_amount += line.currency_id._convert_payroll(
                            line.total, self._get_fiscal_currency(), contract_obj.company_id, payslip.rate_id.name or fields.Date.today())
                    else:
                        pass
                if paid and not payslip.vac_paid:
                    payslip.vac_paid = True
                else:
                    pass
        else:
            pass

        if contract_obj.employee_holiday_advance and contract_obj.employee_holiday_depresvac_amount and contract_obj.employee_vacation_bonus:
            contract_obj.employee_total_holiday_advance = (contract_obj.employee_holiday_advance + contract_obj.employee_vacation_bonus) - \
                contract_obj.employee_holiday_depresvac_amount
        elif contract_obj.employee_holiday_advance and contract_obj.employee_vacation_bonus:
            contract_obj.employee_total_holiday_advance = contract_obj.employee_holiday_advance + \
                contract_obj.employee_vacation_bonus
        elif contract_obj.employee_holiday_depresvac_amount:
            contract_obj.employee_total_holiday_advance = contract_obj.employee_holiday_depresvac_amount
        else:
            contract_obj.employee_total_holiday_advance = 0

    # Employee loans
    def _compute_employee_loans(self, payslip_obj, contract_obj):
        # salary advance
        aux_sum = []
        list_advance = contract_obj.salary_advance_ids.filtered(lambda x: x.reason in ['5','3'] and x.state in ['approved'])
        for line in list_advance:
            currency = self._get_fiscal_currency()
            date = line.rate_id.name or fields.Date.today()
            if line.currency_id != currency and not line.rate_id:
                val_sum = currency._convert_payroll(line.advancement, line.currency_id, contract_obj.company_id, date)
            else:
                val_sum = line.currency_id._convert_payroll(line.advancement, currency, contract_obj.company_id, date)

            aux_sum.append(val_sum)

        advancement_bs = sum(aux_sum)
        contract_obj.employee_loans = advancement_bs

        if contract_obj.employee_loans and contract_obj.employee_dpres:
            contract_obj.employee_result_loans = contract_obj.employee_loans - contract_obj.employee_dpres
            
        elif contract_obj.employee_loans:
            contract_obj.employee_result_loans = contract_obj.employee_loans

        elif contract_obj.employee_dpres:
            contract_obj.employee_result_loans = contract_obj.employee_dpres

        else:
            contract_obj.employee_result_loans = 0

    #Calcular Deuda Total
    @api.depends('employee_loans', 'salary_advance_ids')
    def _compute_employee_dpres(self):
        # La moneda del contrato
        for rec in self:
            currency = self._get_fiscal_currency()
            pagado = 0        
            
            for debt in rec.salary_advance_ids:
                date = debt.rate_id.name or fields.Date.today()
                
                if debt.state == "approved":        
                    for pay in debt.payments_links_ids:
                        if pay.currency_id != currency:
                            if debt.currency_id != currency and not debt.rate_id:
                                pagado += currency._convert_payroll(pay.quote_amount, debt.currency_id, rec.company_id, date)
                            else:
                                pagado += pay.quote_amount * debt.rate_amount

                        else:
                            pagado += pay.quote_amount
            rec.employee_dpres = pagado

    #Calcular Deuda Total
    @api.depends('employee_loans', 'salary_advance_ids')
    def _compute_employee_next_cuota(self):
        # La moneda del contrato
        for rec in self:
            a_pagar = 0
            for debt in rec.salary_advance_ids:
                #---#
                if debt.state == "approved" and debt.active_advance and debt.reason in ['3', '5']:
                    quote_converted = 0
                    currency = self._get_fiscal_currency()
                    date = debt.rate_id.name or fields.Date.today()
                    if debt.currency_id != currency and not debt.rate_id:
                        quote_converted = currency._convert_payroll(debt.quote_amount, debt.currency_id, rec.company_id, date)

                    a_pagar += debt.quote_amount if not quote_converted else quote_converted 
                #---#

            rec.next_cuota = a_pagar
    #//


    # Update advances button
    # FIXME: REFACTOR: utilidades, prestamos, vacaiones
    def update_advances(self):
        # from the button
        self._compute_employee_dpres()
        if self.active:
            current_contract = self._get_current_contract(self.employee_id)
            if current_contract:
                seniority = current_contract._get_employee_seniority()

                current_contract.employee_months_seniority = seniority.get('months')
                current_contract.employee_years_seniority = seniority.get('years')
                current_contract.employee_days_seniority = seniority.get('days')

                # Searching for the employee's payroll that is in paid or done status.
                payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id), ('state', 'in', [
                    'done', 'paid'])], order='id desc')
                        
                self._compute_employee_loans(payslip_obj, current_contract)
                self._compute_employee_holiday_advance(payslip_obj, current_contract)


    @api.depends('salary_advance_ids')
    def _vaction_advances_calculation(self):
        for rec in self:
            total_pagar = 0
            a_pagar = 0
            bono_pagar = 0
            complete_pagar = 0

            for debt in rec.salary_advance_ids:
                #---#
                if debt.reason in ['4']:
                    quote_converted = 0
                    total_converted = 0
                    currency = self._get_fiscal_currency()
                    date = debt.rate_id.name or fields.Date.today()
                    if debt.currency_id != currency and not debt.rate_id:
                        quote_converted = currency._convert_payroll(debt.quote_amount, debt.currency_id, rec.company_id, date)
                        total_converted = currency._convert_payroll(debt.advancement, debt.currency_id, rec.company_id, date)

                    complete_pagar += debt.advancement if not total_converted else total_converted 
                    
                    if debt.state == "approved" and debt.active_advance:
                        if debt.advance_vacation:
                            bono_pagar += debt.advancement if not total_converted else total_converted 

                        else:
                            total_pagar += debt.advancement if not total_converted else total_converted 
                            a_pagar += debt.quote_amount if not quote_converted else quote_converted 
                #---#

            rec.employee_holiday_advance = total_pagar
            rec.employee_vacation_bonus = bono_pagar
            rec.employee_holiday_depresvac_amount = a_pagar
            rec.employee_total_holiday_advance = complete_pagar

