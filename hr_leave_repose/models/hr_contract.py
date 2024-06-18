from odoo import models
from dateutil import relativedelta
import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _get_work_hours(self, date_from, date_to, domain=None):
        res = super(HrContract, self)._get_work_hours(
            date_from, date_to, domain=domain)

        self._add_leaves(res, date_from, date_to)
        self._recalculte_leaves(res, date_from, date_to)
        return res

    def _add_leaves(self, res, date_from, date_to):
        # if "res" not bring a leave repose, add the line of all leaves in the interval

        # excluding vacation
        vac = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE190')]).id

        calendar_leave = self.resource_calendar_id.leave_ids.filtered(
            lambda x:   x.holiday_id.holiday_status_id.work_entry_type_id.id not in res.keys()
            and x.holiday_id.employee_id.id == self.employee_id.id
            and x.holiday_id.full_paid == False
            and date_to >= x.holiday_id.request_date_from
            and x.holiday_id.holiday_status_id.work_entry_type_id.id != vac
        )

        if calendar_leave:
            leaves = [calendar.holiday_id for calendar in calendar_leave]
            dict_leave = {
                l.holiday_status_id.work_entry_type_id.id: 0 for l in leaves}

            res.update(dict_leave)


    def _recalculte_leaves(self, res, date_from, date_to):
        # recalculate assitances and time offs
        attendance_key = 0
        attendance_hours_rest = 0
        hours_weekend = 0
        hours_per_day = self.resource_calendar_id.hours_per_day

        vacation = self.env['hr.work.entry.type'].search(
            [('code', '=', 'LEAVE190')])
        holidays = self.env['hr.work.entry.type'].search(
            [('code', '=', 'LEAVE300')])
        holidays_hours = res.get(holidays.id, False)

        delete_res = []

        for val in res.items():
            work_entry = self.env['hr.work.entry.type'].search(
                [('id', '=', val[0])])
            if work_entry.is_leave:
                leaves = self.resource_calendar_id.leave_ids
                type_leaves = leaves.filtered(
                    lambda x: 
                    x.holiday_id.holiday_status_id.work_entry_type_id.id == val[0]
                    and x.holiday_id.employee_id.id == self.employee_id.id
                    and x.holiday_id.full_paid == False
                    and date_to >= x.holiday_id.request_date_from
                )

                hours = 0
                for l in type_leaves:
                    hours_days = (  l.holiday_id.holiday_status_id.request_unit != 'day' \
                                    and not l.holiday_id.request_unit_half \
                                    and not l.holiday_id.request_unit_hours )
                    
                    if l.holiday_id.holiday_status_id.request_unit == 'day' or hours_days:
                        aux_hours, attendance_hours_rest = self._leave_by_days(l, date_from, date_to, res, hours_per_day)
                        hours_weekend += abs(attendance_hours_rest)
                        hours += aux_hours
                    else:
                        hours += l.holiday_id.number_of_hours_display
                        if l.holiday_id.count_weekend and l.holiday_id.request_date_from.weekday() in [5, 6]:
                            hours_weekend += abs(l.holiday_id.number_of_hours_display)
                            
                    if holidays_hours and val[0] == vacation.id:
                        hours -= holidays_hours

                if val[1] != hours and type_leaves:
                    aux = abs(val[1] - hours)
                    attendance_hours_rest += aux

                    # TODO: select_period store the complete time including weekends, this could change
                    # aux_days = self._exclude_weekends_days(date_to - date_from, (date_from, date_to))
                    select_period = (
                        ((date_to - date_from).days + 1)) * hours_per_day

                    res[val[0]] = hours if select_period >= hours else select_period

                # delete if theres no leave and not is a holiday
                if not type_leaves and work_entry.code != 'LEAVE300':
                    delete_res.append(val[0])

            else:
                try:
                    if "WORK100" in work_entry.code.upper():
                        attendance_key = val[0]
                except:
                    pass

        if attendance_hours_rest != 0 and attendance_key != 0:
            # the number of days of assitances can't be minor than 0
            if res[attendance_key] - attendance_hours_rest > 0:
                res[attendance_key] -= attendance_hours_rest
            else:
                res[attendance_key] = 0

            if res[attendance_key] == 0:
                del res[attendance_key]

        #delete all invalid leaves
        for d in delete_res:
            del res[d]

        delta_day = relativedelta.relativedelta(date_to, date_from).days
        if date_to.day == 31 and delta_day in [15, 30]:
            date_to = date_to.replace(day=30)

        total_hours = sum(res.values()) - hours_weekend
        all_days = 0
        current = date_from
        while current <= date_to:
            if current.weekday() not in [5, 6]:
                all_days += 1
                
            current += datetime.timedelta(days=1)

        #FIXME: error si se usa un periodo corto, sin asistencias y cargado de otras ausencias
        all_hours = all_days * hours_per_day
        dif = all_hours - total_hours
        if dif > 0:
            if attendance_key != 0:
                res[attendance_key] += dif

            else:
                work_id = self.env['hr.work.entry.type'].search([('code', '=', 'WORK100')]).id
                res.update({work_id: dif})


    def _leave_by_days(self, calendar_leave, date_from, date_to, res, hours_per_day):
        leave = calendar_leave.holiday_id
        leave_date_from = leave.request_date_from

        # moving start date to days without paying
        i = 0
        while i < leave.days_paid:
            leave_date_from += datetime.timedelta(days=1)
            if not leave.count_weekend and leave_date_from.weekday() in [5,6]:
                continue
            i += 1

        if leave.holiday_status_id.work_entry_type_id.code == 'LEAVE190':
            leave_date_from = date_from

        in_intersection = self._exist_intersection(date_from, date_to,
                                                    calendar_leave.date_from.date(),
                                                    calendar_leave.date_to.date())
        hours = 0
        hours_rest = 0

        if in_intersection:
            # get interval when leave days are used in this payslips
            interseccion = (max(date_from, leave_date_from),
                            min(date_to, leave.request_date_to))
            duracion = interseccion[1] - interseccion[0]

            if leave.count_weekend:
                days = duracion.days + 1 if duracion.days >= 0 else 0
                hours_rest -= self._recalculate_weekend_days(
                    interseccion)

            else:
                # if weekend dont' count in this calculate, have to subtract it
                excluded_days = self._exclude_weekends_days(
                    duracion, interseccion)
                days = duracion.days + 1 - excluded_days

            if leave.holiday_status_id.work_entry_type_id.code != 'LEAVE190':
                days = self._add_left_leave_days(
                    days, interseccion, res, leave, date_from, date_to)

            hours += days * hours_per_day

        else:
            hours += (leave.number_of_days -
                        leave.days_paid) * hours_per_day
            
        return hours, hours_rest


    def _recalculate_weekend_days(self, interseccion):
        # count the numbers of weekends in the interval
        count_leave_weekend = 0
        current_day = interseccion[0]

        while current_day <= interseccion[1]:
            if current_day.weekday() in [5, 6]:
                count_leave_weekend += 1
            current_day += datetime.timedelta(days=1)

        hours_leave_weekend = count_leave_weekend * \
            self.resource_calendar_id.hours_per_day
        return hours_leave_weekend

    def _add_left_leave_days(self, days, interseccion, res, leave, slip_date_from, slip_date_to):
        # if there are days that wasn't paid yet, there will sum but just when there are assitances days in the period selected
        aux_day = days
        leave_date_from = leave.request_date_from

        if leave_date_from < slip_date_from and 1 in res:
            date = min(slip_date_from, leave.request_date_to)
            duracion = date - leave_date_from
            aux_day = duracion.days + (1 if date != slip_date_from else 0)

            if not leave.count_weekend:
                # if weekend dont' count in this calculate, have to subtract it
                aux_day -= self._exclude_weekends_days(
                    duracion, (leave_date_from, date))

            aux_day -= leave.days_paid

            aux_day += days

        delta_day = (slip_date_to - slip_date_from).days + 1
        if aux_day > delta_day:
            aux_day = delta_day
        aux_day -= 1 if interseccion[1].day == 31 and delta_day == 16 else 0

        return aux_day

    def _exist_intersection(self, date_from, date_to, leave_date_from, leave_date_to):
        # if the dates intersect, return True
        interseccion = (max(date_from, leave_date_from),
                        min(date_to, leave_date_to))
        duracion = interseccion[1] - interseccion[0]

        return True if duracion.days + 1 > 0 else False

    def _exclude_weekends_days(self, duracion, interseccion):
        # if weekend dont' count in this calculate, have to subtract it
        excluded_days = 0

        for day in range((duracion).days + 1):
            current_date = interseccion[0] + datetime.timedelta(day)
            if current_date.weekday() in [5, 6]:
                excluded_days += 1

        return excluded_days

