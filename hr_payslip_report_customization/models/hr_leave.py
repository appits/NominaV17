# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError, ValidationError


def number_of_weekend_days(date1, date2):
    weekend_days = 0
    total_days = 0
    current_date = date1
    while current_date <= date2:
        if current_date.weekday() in [5, 6]:
            weekend_days += 1
        else:
            total_days += 1 
        current_date += timedelta(days=1)
    return weekend_days,total_days



class hrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.depends('date_from','date_to')
    def _compute_number_of_weekend_days(self):
        for rec in self:
            rec.weekend_days_hr = 0
            rec.work_days_hr = 0
            rec.holidays_number_hr = 0
            rec.work_days_aditionales  = 0
            rec.work_days_legales = 0
            if rec.is_holiday_nomina:
                
                if rec.date_from and rec.date_to:
                    date_from = rec.request_date_from
                    date_to = rec.request_date_to
                    rec.weekend_days_hr, dias_vacaciones  =  number_of_weekend_days(date_from, date_to)
                    rec.holidays_number_hr = self._compute_number_holidays_in_date(date_from, date_to) 
                    rec.work_days_hr = dias_vacaciones - rec.holidays_number_hr 
                    if rec.work_days_hr > 15:
                        rec.work_days_legales = 15
                        rec.work_days_aditionales  =  rec.work_days_hr - 15
                    else:
                        rec.work_days_legales = rec.work_days_hr
        


    @api.depends('holiday_status_id')
    def _compute_is_holiday_nomina(self):
        for rec in self:
            rec.is_holiday_nomina = False
            if rec.holiday_status_id and rec.holiday_status_id.work_entry_type_id.code == "LEAVE190":
                rec.is_holiday_nomina = True
                
            
    @api.depends('date_from','date_to')
    def compute_lista_feriados(self,date1, date2, search_holidays_all):
        
        date_list = []
        d = date1
        while d <= date2:
            date_list.append(d.strftime("%d-%m-%Y"))
            d += timedelta(days=1)
        dias_feriado = 0
        for fecha in date_list:
            fecha = datetime.strptime(fecha, '%d-%m-%Y').date()
            dia_es_feriado = search_holidays_all.filtered(lambda x:\
                            (x.date_to.date() > fecha and x.date_from.date() < fecha)\
                                or (x.date_to.date() == fecha) or\
                                (x.date_from.date() == fecha))

            if dia_es_feriado and fecha.weekday() not in [5, 6]:
                dias_feriado += 1

                print(fecha)
                print(dias_feriado)
        return dias_feriado

    @api.depends('date_from')
    def _compute_number_holidays_in_date(self, date_from, date_to):
        for rec in self:
            
            search_holidays_all = rec.env['resource.calendar.leaves'].search([])

            search_holidays_all = search_holidays_all.filtered(lambda x: ( x.work_entry_type_id.name ) and ( 'feriado' in x.work_entry_type_id.name.lower() ) )
            if rec.date_to and rec.date_from :
                date_to = rec.date_to.date()
                date_from = rec.date_from.date()
                company_id = self.env.company.id
                search_holidays = search_holidays_all.filtered(lambda x:\
                                ( x.date_to.date() >= date_to and x.date_from.date() <= date_to) and (company_id == x.company_id.id)
                                )

                dias_feriado = rec.compute_lista_feriados(date_from , date_to, search_holidays_all)
            
            return dias_feriado
        

    hr_payslip_custom_id = fields.Many2one('hr.payslip',string='Ausencia en Payslip',store=True)

    is_holiday_nomina = fields.Boolean(
        string='Es Vacaciones',
        store=True,
        compute="_compute_is_holiday_nomina")

    weekend_days_hr = fields.Integer(
        string='Dias de Descanso',
        store=True,
        compute="_compute_number_of_weekend_days")

    work_days_legales = fields.Integer(
        string='Vaciones Leagales',
        store=True,
        compute="_compute_number_of_weekend_days")


    work_days_hr = fields.Integer(
        string='Dias Vacaciones',
        store=True,
        compute="_compute_number_of_weekend_days")

    work_days_aditionales = fields.Integer(
        string='Dias Adicionales',
        store=True,
        compute="_compute_number_of_weekend_days")


    holidays_number_hr = fields.Integer(
        string='Dias Feriados',
        store=True,
        compute="_compute_number_holidays_in_date")

