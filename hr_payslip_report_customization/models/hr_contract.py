from odoo import models, fields, api, _
from dateutil import relativedelta
import datetime

class HrContract(models.Model):
    _inherit = 'hr.contract'

    #TODO: REFACTOR
    def _get_work_hours(self, date_from, date_to, domain=None): 
        date = self._date_to_change(date_to, date_from)
        return super(HrContract, self)._get_work_hours(date_from, date, domain=domain)


    def _date_to_change(self, date_to, date_from):
        date = date_to
        delta_day = relativedelta.relativedelta(date_to, date_from).days

        # si es la segunda quincena y acaba en un 31, se resta un dia
        if date_to.day == 31 and delta_day in [15, 30]:
            date = date_to.replace(day=30)

        # si es la segunda quincena y es febrero, se suma los dias respectivos
        elif date_to.month == 2 and date_to.day in [28, 29] and delta_day in [12, 13, 27, 28]:
            d = 30 - date_to.day
            i = 0
            while i != d:
                date += datetime.timedelta(days=1)
                if date.weekday() not in [5, 6]:
                    i += 1

        return date