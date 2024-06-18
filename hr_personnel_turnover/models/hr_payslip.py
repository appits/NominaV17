from odoo import models, api, fields, _
from datetime import datetime
import json

class HrPayslip(models.Model):
    _inherit = "hr.payslip"


    def action_payslip_paid(self):
        super(HrPayslip, self).action_payslip_paid()

        vals = []
        for payslip in self:
            if payslip.is_holiday_nomina:
                val = payslip._prepare_turnover_vals()
                vals.append(val)

        self.env['hr.personnel.turnover'].create(vals)


    def _prepare_turnover_vals(self):
        field_name = self.env['ir.translation'].get_field_string(self.contract_id._name)['average_salary']
        value = self.contract_id.average_salary

        origin = json.dumps({'hr.payslip': self.id})
        changed_field = json.dumps({'average_salary': value})

        val = {
            'company_id': self.env.company.id,
            'state': 'validate',
            'user_validate': self.env.user.id,
            'validate_date': datetime.now(),
            'employee_id': self.employee_id.id,
            'contract_id': self.contract_id.id,
            'reason': "vacation",
            'move_type': "in",
            'description': _("Period: ") + self.period_holidays,
            'origin': origin,
            'changed_field': changed_field,
            'field_name': field_name,
            'field_value': str(value),
        }

        return val
