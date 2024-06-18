from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WizardReportINCES(models.TransientModel):
    _name = "wizard.report.inces"
    _description = "INCES report wizard Model"
    
    def _get_today(self):
        return fields.Date.from_string(fields.Date.today())
    
    
    p = [   ("one", "Monthly"),
            ("three", "Quarterly")]

    q = [   ("q1", "1st Quarter"),
            ("q2", "2nd Quarter"),
            ("q3", "3rd Quarter"),
            ("q4", "4th Quarter")]
    
    period = fields.Selection(string="Period", selection=p, default="one")
    quarter = fields.Selection(string="Quarter", selection=q, default="q1")
    date = fields.Date(string="Date", default=_get_today)
    contract_ids = fields.Many2many("hr.contract")
    date_msg = fields.Boolean()
    months_display = fields.Char()


    @api.onchange("date", "period")
    def _get_months(self):
        data = self._get_month_names().keys()
        self.months_display = ", ".join(data)


    @api.onchange("date")
    def _onchange_date_msg(self):
        today = self._get_today()
        self.date_msg = True if self.date.month >= today.month else False


    @api.onchange("period", "quarter")
    def _onchange_quarter(self):
        if self.period == "three":
            today = self._get_today()
            if self.quarter == "q1":
                month = 3
            elif self.quarter == "q2":
                month = 6
            elif self.quarter == "q3":
                month = 9
            else:
                month = 12

            self.date = today.replace(month=month)


    def print_inces_report(self):
        if self.date_msg:
            raise ValidationError(_("Date selected is not valid"))

        self.contract_ids = self.contract_ids.search([])

        return self.env.ref('payslip_details_custom_itsales.inces_report_action').report_action(self)


    def _get_month_names(self):
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

        nombres = {}
        if self.period == "one":
            nombre = spanish_month_names[self.date.month]
            nombres.update({nombre: self.date}) 
        else:
            nro_month = self.date.month
            for i in range(nro_month-2, nro_month+1):
                nombre = spanish_month_names[i]
                date = self.date.replace(month=i)

                nombres.update({nombre: date}) 

        return nombres
