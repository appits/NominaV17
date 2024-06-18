from odoo import models, fields, api, _
import datetime
import json

# Add here all the worked_days' code related to leave that want to have this behavior
# rpose codes:
LEAVE_CODE = [
    'LEAVE111',
    'LEAVE109',
    'LEAVE122',
]

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    days_res = fields.Integer(default=0, copy=False)
    days_res_left = fields.Integer(default=0, copy=False)
    original_days_leave = fields.Char(default="{}")

    #TODO: REFACTOR
    @api.depends("date_to", "date_from")
    def _get_search_leaves_all(self):
        """Extraer Lista de Ausencias Totales dentro 
        y fuera del Periodo

        Returns:
            Recorset: Dias de ausencias dentro y fuera de Periodo
        """
        for rec in self:
            if rec.date_to and rec.date_from:
                vacation = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE190')])
                leave_type = self.env['hr.leave.type'].search([('work_entry_type_id', '=', vacation.id)])

                try:
                    date_to = rec.date_to.date()
                except:
                    date_to = rec.date_to

                search_leaves_all = rec.env["hr.leave"].search([
                    ('holiday_status_id', 'not in', leave_type.ids),
                    ("state", "in", ["validate"]),
                    ("full_paid", "=", False),
                    ("payslip_state", "in", ["normal", "blocked",'done']),
                ])

                search_leaves_all = search_leaves_all.filtered( lambda x:   rec.employee_id.id in x.employee_ids.ids \
                                                                            and date_to >= x.request_date_from )

                vac_leave = self.env['hr.leave'].search([
                    ('holiday_status_id', 'in', leave_type.ids),
                    ("payslip_state", "in", ["normal", "blocked", 'done']),
                    ("state", "in", ["validate"]),
                ])

                search_leaves_all += vac_leave.filtered(
                    lambda x:
                    rec.employee_id.id in x.employee_ids.ids
                    and rec.date_to >= x.request_date_from
                    and rec.date_from <= x.request_date_to
                )
                
            return search_leaves_all


    def action_payslip_paid(self):
        for payslip in self:
            work_entry = payslip.worked_days_line_ids.filtered(lambda x: x.code in LEAVE_CODE)
            work_entry_type_ids = [work.work_entry_type_id.id for work in work_entry]
            
            leave = payslip.leaves_all_days_ids.filtered(lambda x: x.holiday_status_id.work_entry_type_id.id in work_entry_type_ids)
            leave = sorted(leave, key=lambda x: (x.date_to,  0 < payslip._get_intersection(payslip.date_from, payslip.date_to, x.request_date_from, x.request_date_to, x.count_weekend)))

            for l in leave:
                if (
                    payslip.name
                    and "rembols" not in payslip.name.lower()
                    and payslip.struct_id
                    and "prestamo" not in payslip.name.lower()
                    and l.full_paid == True
                ):
                    l.write({ 'orignal_leave_days': 0, 'payslip_state': "done"})
                else:
                    l.write({ 'orignal_leave_days': 0 })

        super(HrPayslip, self).action_payslip_paid()


    def action_payslip_done(self):
        # calculate the leave days that going to be paid in the slip
        # -- select all days that wan't paid in particular leave and add it into the period
        for payslip in self:
            # to know if exist vacation days
            vacation = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE190')])
            work_entry_vac = payslip.worked_days_line_ids.filtered(lambda x: x.work_entry_type_id.id == vacation.id)

            work_leave_id = [l.holiday_status_id.work_entry_type_id.id for l in payslip.leaves_all_days_ids]
            work_entry = payslip.worked_days_line_ids.filtered(lambda x: x.work_entry_type_id.id in work_leave_id)
            work_entry_days = sum([ work.number_of_days for work in work_entry ])

            leave = payslip.leaves_all_days_ids
            leave = sorted(leave, key=lambda x: (x.date_to,  0 < payslip._get_intersection(payslip.date_from, payslip.date_to, x.request_date_from, x.request_date_to, x.count_weekend)))

            for l in leave:
                leave_json = json.loads(payslip.original_days_leave)
                leave_json.update({l.id: l.days_paid})
                payslip.original_days_leave = json.dumps(leave_json)

                if l.holiday_status_id.request_unit == "days":
                    interseccion = (max(payslip.date_from, l.request_date_from), min(payslip.date_to, l.request_date_to))
                    duracion = payslip._get_intersection(payslip.date_from, payslip.date_to, l.request_date_from, l.request_date_to, l.count_weekend)
                    duracion = payslip.contract_id._add_left_leave_days(duracion, interseccion, {1: 0}, l, payslip.date_from, payslip.date_to)
                else:
                    duracion = l.number_of_days

                if duracion >= work_entry_days or duracion <= 0:
                    duracion = work_entry_days
                
                paid = l.days_paid + duracion

                work_entry_days -= duracion

                if not work_entry_vac:
                    # in theory and following the flow,
                    # if "is_holiday_nomina" check is active, 
                    # is because in this payslip there would be only one leave (vacation) 
                    if not l.full_paid and paid >= l.number_of_days:
                        paid = l.number_of_days
                        l.write({ 'days_paid': paid, 'full_paid': True })
                    else:
                        l.write({ 'days_paid': paid })
        
        super(HrPayslip, self).action_payslip_done()


    def compute_sheet(self):
        # to calculate some concepts related to reposes, catch the first 3 leave days for each leaves detected
        # -- can catch it if the days aren't continues
        for payslip in self:
            work_entry = payslip.worked_days_line_ids.filtered(lambda x: x.code in LEAVE_CODE)
            work_entry_days = sum([work.number_of_days for work in work_entry])

            work_entry = [w.work_entry_type_id.id for w in work_entry]
            leave = payslip.leaves_all_days_ids.filtered(lambda x: x.holiday_status_id.work_entry_type_id.id in work_entry)
            leave = sorted(leave, key=lambda x: (x.date_to,  0 < payslip._get_intersection(payslip.date_from, payslip.date_to, x.request_date_from, x.request_date_to, x.count_weekend)))

            flag = True
            for l in leave:

                interseccion = (max(payslip.date_from, l.request_date_from), min(payslip.date_to, l.request_date_to))
                duracion = payslip._get_intersection(payslip.date_from, payslip.date_to, l.request_date_from, l.request_date_to, l.count_weekend)
                duracion = payslip.contract_id._add_left_leave_days(duracion, interseccion, {1: 0}, l, payslip.date_from, payslip.date_to)


                payslip._clean_values(l, flag)
                if flag: flag = not flag

                if duracion <= 0:
                    duracion = work_entry_days

                if not l.extend_leave:
                    l.orignal_leave_days = l.paid_res
                    l.paid_res -= duracion
                    
                    payslip.days_res_left += abs(l.paid_res if l.paid_res < 0 else 0)
                    l.paid_res = l.paid_res if l.paid_res > 0 else 0

                    payslip.days_res += l.orignal_leave_days - l.paid_res      
                else:
                    payslip.days_res_left += duracion
                    l.orignal_leave_days = 3
                    l.paid_res = 0

                work_entry_days -= duracion
        
        super(HrPayslip, self).compute_sheet()


    def action_payslip_cancel(self):
        for payslip in self:
            payslip._clean_values()
        super(HrPayslip, self).payslip_cancel()


    def _clean_values(self, leave=None, clean=True, jump=False):
        # reset values from the slip and leaves, this let to recalculate concept's sheet (hr.payslip.line)
        if not leave:
            work_entry = [work.work_entry_type_id.id for work in self.worked_days_line_ids]
            leave = self.leaves_all_days_ids.filtered(lambda x: x.holiday_status_id.work_entry_type_id.id in work_entry)
            leave = sorted(leave, key=lambda x: (x.date_to,  0 < self._get_intersection(self.date_from, self.date_to, x.request_date_from, x.request_date_to, x.count_weekend)))

        for l in leave:

            if self.state == "done":
                leave_json = json.loads(self.original_days_leave)
                unpaid = leave_json[str(l.id)]
                if not jump:
                    del leave_json[str(l.id)]
                self.original_days_leave = json.dumps(leave_json)

            else:
                unpaid = l.days_paid

            
            val = l.paid_res if l.orignal_leave_days == 0 else l.orignal_leave_days
            l.write ({
                        'full_paid': False,
                        'days_paid': unpaid,
                        'paid_res': val,
                        'orignal_leave_days': 0
                    })

        if clean:
            self.days_res = 0
            self.days_res_left = 0


    def _get_monday_saturday_sunday_numbers(self):
        # function to reduce the number of weekends days in the period if a leave it's detected
        res = super()._get_monday_saturday_sunday_numbers()

        leave = self.compute_leaves_all_days_ids()
        for l in leave:
            if l.count_weekend:
                count_leave_weekend = 0
                interseccion = (max(self.date_from, l.request_date_from), min(self.date_to, l.request_date_to))
                current_day = interseccion[0]

                while current_day <= interseccion[1]:
                    if current_day.weekday() in [5, 6]:
                        count_leave_weekend += 1
                    current_day += datetime.timedelta(days=1)
                
                res['saturdays_sunday_numbers'] -= count_leave_weekend
                if res['saturdays_sunday_numbers'] < 0:
                    res['saturdays_sunday_numbers'] = 0

            #TODO: this may been in other module, it's related to vaction stuff in #2225
            vacation_leave = ["LEAVE190"]
            if l.holiday_status_id.work_entry_type_id.code in vacation_leave and not self.is_holiday_nomina:
                count_leave_mondays = 0
                interseccion = (max(self.date_from, l.request_date_from), min(self.date_to, l.request_date_to))
                current_day = interseccion[0]

                while current_day <= interseccion[1]:
                    if current_day.weekday() in [0]:
                        count_leave_mondays += 1
                    current_day += datetime.timedelta(days=1)
                
                res['monday_numbers'] -= count_leave_mondays
                if res['monday_numbers'] < 0:
                    res['monday_numbers'] = 0
            
        return res


    def _get_intersection(self, date_from, date_to, leave_date_from, leave_date_to, count_weekend=True):
        # if the dates intersect, retorn the number of days
        interseccion = (max(date_from, leave_date_from), min(date_to, leave_date_to))
        duracion = interseccion[1] - interseccion[0]

        days = duracion.days + 1

        if not count_weekend:
            dias_excluidos = 0
            for day in range(days):
                current_date = interseccion[0] + datetime.timedelta(day)
                if current_date.weekday() not in [5, 6]:
                    dias_excluidos += 1

            days = dias_excluidos

        return days


    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        # when the holidays are in leave period, there have to discount days in holidays
        res = super(HrPayslip, self)._get_worked_day_lines(domain, check_out_of_contract)
        all_leaves = self._get_search_leaves_all()

        holiday_work_day = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE300')]).id
        work_day = self.env['hr.work.entry.type'].search([('code', '=', 'WORK100')])

        hours_per_day = self._get_worked_day_lines_hours_per_day()
        res_work_days = {r['work_entry_type_id']: i for i, r in enumerate(res)}

        leave = all_leaves.filtered(lambda x: x.holiday_status_id.work_entry_type_id.code in LEAVE_CODE)
        if leave:
            leave = sorted(leave, key=lambda x: (x.date_to,  0 < self._get_intersection(self.date_from, self.date_to, x.request_date_from, x.request_date_to, x.count_weekend)))

            leave_date_start = max(leave[0].request_date_from, self.date_from)
            leave_date_end = min(leave[-1].request_date_to, self.date_to)

            holidays_days = self._holidays_in_period(leave_date_start, leave_date_end)

            if holidays_days:
                try:
                    res_assits = res[ res_work_days[work_day.id] ]
                except:
                    res_assits = None
                res_holiday = res[ res_work_days[holiday_work_day] ]

                holidays_hours = holidays_days * hours_per_day

                res_holiday['number_of_days'] -= holidays_days
                res_holiday['number_of_hours'] -= holidays_hours

                if res_holiday['number_of_days'] <= 0:
                    res.pop( res_work_days[holiday_work_day] )
                
                period_days = (self.date_to - self.date_from).days + 1
                if self.date_to.day == 31 and period_days == 16:
                    period_days -= 1
                period_days -= self.saturdays_sunday_numbers
                sum_days = sum([w['number_of_days'] for w in res])
                
                if res_assits:
                    res_assits['number_of_days'] += holidays_days
                    res_assits['number_of_hours'] += holidays_hours
                else:
                    if sum_days < period_days:
                        res.append({
                            'sequence': work_day.sequence,
                            'work_entry_type_id': work_day.id,
                            'number_of_days': holidays_days,
                            'number_of_hours': holidays_hours,
                        })

        return res


    def _holidays_in_period(self, date_start, date_end):
        holidays_code = ['LEAVE300'] 
        holiday_work_day = self.env['hr.work.entry.type'].search([('code', 'in', holidays_code)])

        holidays = self.env['resource.calendar.leaves'].search([
                                                            ('work_entry_type_id', 'in', holiday_work_day.ids),
                                                            ('date_from', '>=', date_start),
                                                            ('date_from', '<=', date_end),
                                                        ])
        
        count_holidays = 0
        for h in holidays:
            count_holidays += self._get_intersection(date_start, date_end, h.date_from.date(), h.date_to.date(), False)

        return count_holidays