from odoo import models
from dateutil import relativedelta

class HrWorkEntry(models.Model):
    _inherit = "hr.work.entry"

    # las entradas deben tener la cantidad de horas de la ausencia
    def _compute_duration(self):
        super(HrWorkEntry, self)._compute_duration()
        for record in self:
            new_delta_hours = relativedelta.relativedelta(record.date_stop, record.date_start).hours
            if record.duration != new_delta_hours and record.leave_id:
                record.duration = new_delta_hours