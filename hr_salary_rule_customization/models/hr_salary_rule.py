from odoo import fields, models, _
from odoo.tools.safe_eval import safe_eval

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    active_duration = fields.Boolean(string="Active duration")
    duration = fields.Float()
    time_type = [
                ('d', 'Days'),
                ('m', 'Months'),
                ('y', 'Years'),
                ('h', 'Hours'),
            ]
    type_duration = fields.Selection(time_type, string="Time unit", default="d", help="Select the time unit to this value")
    duration_python = fields.Text(string='Python duration',
        default='''
# Available variables:
#----------------------
# payslip: object containing the payslips
# employee: hr.employee object
# contract: hr.contract object
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
# worked_days: object containing the computed worked days
# inputs: object containing the computed inputs.

# Note: 
#   returned value have to be set in the variable 'result'
#   result = 0 is default value to represent NULL

result = 0 ''',
        help='Applied this rule for time calculation if condition is true.')
    

    def _compute_duration(self, localdict):
        """
        :param localdict: dictionary containing the current computation environment
        :return: returns a duration
        :rtype: float
        """
        self.ensure_one()
        if self.active_duration:
            try:
                safe_eval(self.duration_python or 0.0, localdict, mode='exec', nocopy=True)
                self.duration = localdict.get('result', 0.0)
                return self.duration
            except Exception as e:
                self._raise_error(localdict, _("Wrong python code defined for:"), e)


class HrPayrollEditPayslipLine(models.TransientModel):
    _inherit = 'hr.payroll.edit.payslip.line'

    duration_display = fields.Char(string="Duration")
    duration = fields.Float()
