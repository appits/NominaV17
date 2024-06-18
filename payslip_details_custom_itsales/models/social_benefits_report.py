from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WizardReportPPSS(models.TransientModel):
    _name = "social.benefits.report"
    _description = "ISLR report wizard Model"

    def _get_today(self):
        return fields.Date.from_string(fields.Date.today())

    date = fields.Date(string="Date", default=_get_today)
    msg = fields.Boolean(default=False, compute="_show_msg")
    employee_ids = fields.Many2many('hr.employee', string="Employees", required=True)
    month_name = fields.Char(compute="_set_month_name")
    massive_selection = fields.Boolean(  string="Massive selection", default=False,
                                            help="""
                                                Active this check to bring al employee with ongoing contract.\n
                                                Desactive to clean all selected employees
                                                """)


    @api.depends('date')
    def _set_month_name(self):
        spanish_month_names = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo", 
            4: "Abril", 
            5: "Mayo", 
            6: "Junio",
            7: "Julio", 
            8: "Agosto", 
            9: "Septiembre", 
            10: "Octubre",
            11: "Noviembre", 
            12: "Diciembre"
        }

        self.month_name = spanish_month_names[self.date.month].upper() + ' ' + str(self.date.year)


    def print_ppss_report(self):     
        if self.msg:
            raise ValidationError(_("Chosen date is not valid"))
        return self.env.ref('payslip_details_custom_itsales.ppss_report_action').report_action(self)


    @api.onchange('massive_selection')
    def _get_all_employee(self):
        self.employee_ids = None
        employee_ids = self._get_employee_ids()
        if self.massive_selection:
            self.employee_ids = self.employee_ids.browse(employee_ids)

        return {'domain':{'employee_ids':[('id', 'in', employee_ids)]}}


    def _get_employee_ids(self):
        query = """
            SELECT DISTINCT ON (employee.id)
                employee.id
            FROM hr_contract AS contract
                JOIN hr_employee AS employee ON contract.employee_id = employee.id
            WHERE
                contract.state = 'open'
        """

        self._cr.execute(query)
        data = self.env.cr.fetchall()
        data = [d[0] for d in data]

        return data


    @api.depends('date')
    def _show_msg(self):
        for record in self:
            today = record._get_today()
            record.msg = True if record.date > today else False
