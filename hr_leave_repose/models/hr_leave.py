from odoo import models, fields, api, _
import datetime

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    count_weekend = fields.Boolean(string="Count weekend", default=False, help=_("Active this check to include weekend in the calculation of duration"))
    paid_res = fields.Integer(string="paid rest", default=3)
    full_paid = fields.Boolean(string="Full Paid", default=False)
    days_paid = fields.Float(string="Days paid", default=0)
    orignal_leave_days = fields.Integer(default=0)

    extend_leave = fields.Boolean(string="Extend leave", default=False)


    def default_get(self, fields):
        defaults = super(HrLeave, self).default_get(fields)
        if defaults.get('request_date_from_period', False):
            del defaults['request_date_from_period'] 
        return defaults


    # adicion de los dias sabados y domingos en los calculos de la duracion de la ausencia
    @api.onchange('count_weekend', 'request_date_from', 'request_date_to', 'employee_id', 'holiday_status_id')
    def _recompute_day_with_weekend(self):
        if self.request_date_from and self.request_date_to:
            if self.count_weekend:
                date_from = self.request_date_from - datetime.timedelta(days=1)
                duration = (self.request_date_to - date_from).days

            else:
                resource_calendar_id = self.employee_id.resource_calendar_id or self.env.company.resource_calendar_id
                domain = [
                    ('calendar_id', '=', resource_calendar_id.id),
                    ('display_type', '=', False), 
                ]
                fields = ['dayofweek']
                groupby = ['dayofweek']
                attendances = self.env['resource.calendar.attendance'].read_group(domain, fields, groupby)
                attendances = [int(a['dayofweek']) for a in attendances]

                duration = 0
                current = self.date_from
                while current <= self.date_to:
                    if current.weekday() in attendances:
                        duration += 1
                        
                    current += datetime.timedelta(days=1)

            self.number_of_days = duration
            self.duration_display = duration



    @api.onchange('request_unit_hours', 'request_unit_half')
    def _clean_dates(self):
        self.date_from = None
        self.date_to = None


    @api.depends('number_of_days')
    def _compute_number_of_hours_display(self):
        super(HrLeave, self)._compute_number_of_hours_display()

        for record in self:
            holiday = record.sudo(True)

            holiday.number_of_hours_display = 0
            resource_calendar_id = holiday.employee_id.resource_calendar_id or self.env.company.resource_calendar_id
            hours_work_per_day = resource_calendar_id.hours_per_day

            if holiday.count_weekend and not holiday.request_unit_half and not holiday.request_unit_hours:
                holiday.number_of_hours_display = holiday.number_of_days * hours_work_per_day

            if  holiday.request_date_from and holiday.request_date_to \
                and holiday.date_from and holiday.date_to\
                and holiday.employee_ids and holiday.holiday_status_id\
                and holiday.holiday_status_id.request_unit != 'day':

                date = datetime.datetime.fromordinal(holiday.request_date_from.toordinal())
                date_from = date
                date_to = date
                weekday = date.weekday()

                if holiday.request_unit_half ^ holiday.request_unit_hours:
                    domain = [
                        ('calendar_id', '=', resource_calendar_id.id),
                        ('display_type', '=', False), 
                        ('dayofweek', '=', str(weekday)),
                        '|', ('week_type', '=', '0'), ('week_type', '=', False)
                    ]
                    attendances = self.env['resource.calendar.attendance'].search(domain)
                    if not attendances:
                        continue

                    uncount = 0
                    if holiday.request_unit_half:
                        attendances = attendances[0] if holiday.request_date_from_period == 'am' else attendances[1]

                        hours_from = int(attendances.hour_from)
                        min_from = attendances.hour_from % 1
                        hours_to = int(attendances.hour_to)
                        min_to = attendances.hour_to % 1

                    elif holiday.request_unit_hours:
                        hour_from = float(holiday.request_hour_from)
                        hour_to = float(holiday.request_hour_to)

                        hours_from = int(hour_from)
                        min_from = hour_from % 1
                        hours_to = int(hour_to)
                        min_to = hour_to % 1

                        limit_ini = attendances[0].hour_from
                        limit_break_ini = attendances[0].hour_to
                        limit_break_end = attendances[1].hour_from
                        limit_end = attendances[1].hour_to

                        if (hour_to - hour_from) > 0:
                            if limit_break_ini <= hour_from < limit_break_end:
                                uncount += hour_from - limit_break_ini 
                            elif limit_break_ini < hour_to <= limit_break_end:
                                uncount += limit_break_end - hour_to 

                            if hour_from <= limit_break_ini and hour_to >= limit_break_end:
                                uncount += attendances[1].hour_from - attendances[0].hour_to

                            if hour_from < limit_ini:
                                uncount += limit_ini - hour_from

                            if hour_to > limit_end:
                                uncount += hour_to - limit_end

                    date_from = holiday.date_from.replace(hour=hours_from, minute=int(min_from * 60))
                    date_to = date.replace(hour=hours_to, minute=int(min_to * 60))
                
                    diff_seconds = (date_to - date_from).total_seconds()
                    res = (diff_seconds / 3600) - uncount
                    holiday.number_of_hours_display = 0 if res < 0 else res
                    holiday.number_of_days = holiday.number_of_hours_display / hours_work_per_day

                    if holiday.state in ['draft']:
                        holiday.date_from = date_from
                        holiday.date_to = date_to

                else:
                    holiday._recompute_day_with_weekend()
                    holiday.number_of_hours_display = holiday.number_of_days * hours_work_per_day


    #TODO: this may been in other module, it's related to vaction stuff in #2225
    @api.onchange('number_of_days')
    def _round_by_force(self):
        if  not self.number_of_days or not self.request_date_to or not self.request_date_from or not self.holiday_status_id\
            and self.request_unit_half or self.request_unit_hours:
            return
        
        no_count_holidays = [
            'LEAVE111',
            'LEAVE109',
            'LEAVE122',
        ]

        holidays_code = ['LEAVE300']
        work_entry = self.env['hr.work.entry.type'].search([('code', 'in', holidays_code)])
        holidays = self.env['resource.calendar.leaves'].search([('date_from', '>=', self.request_date_from), ('date_to', '<', self.request_date_to), ('work_entry_type_id', 'in', work_entry.ids)])

        if self.holiday_status_id.work_entry_type_id.code not in no_count_holidays: 
            if self.count_weekend:
                self.number_of_days -= len(holidays)
            else:
                self.number_of_days -= 0.5 * len(holidays)
        else:
            if not self.count_weekend: 
                self.number_of_days += 0.5 * len(holidays)

        hours_work_per_day = self.employee_id.contract_id.resource_calendar_id.hours_per_day
        self.number_of_hours_display = self.number_of_days * hours_work_per_day


    #TODO: this may been in other module, it's related to vaction stuff in #2225
    @api.onchange('holiday_status_id')
    def _count_weekend_in_vacation(self):
        if self.is_holiday_nomina:
            self.count_weekend = True


    #TODO: this may been in other module, it's related to vaction stuff in #2225
    @api.constrains('holiday_status_id')
    def _count_weekend_in_vacation_constrains(self):
        for record in self:
            if record.is_holiday_nomina:
                record.write({'count_weekend': True})
                
