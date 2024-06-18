from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, MissingError
import calendar


class WizardReportBanavih(models.TransientModel):
    _name = "wizard.report.banavih"
    _description = "Banavih report wizard Model"

    start_date = fields.Date(string="From date")
    end_date = fields.Date(string="To date")
    LPVH = fields.Boolean(string="RPE")
    contract_ids = fields.Many2many("hr.contract")
    salary_structure_type = fields.Many2many("hr.payroll.structure", string="Salary structure type")

    order_table_by = fields.Selection(
        selection = [('registration_number','Receipt'),
                     ('identification_id','Identification Number'),
                     ('name','Name'),
                     ('birthday','Birth Date'),],
        string='Order by',
        default='registration_number',
    )
    
    
    # This modified query includes the end date, and also considers the selected salary structures
    def _get_banavih_contracts(self, start_date, end_date, salary_struct_ids):
        """
            This function gets the employee contracts from the database.

            :param:
                start_date: start date to limit the employee contracts we are getting.
                end_date: end date to limit the employee contracts we are getting.
                salary_struct_ids: a list of integers that contains the ids of the salary structures

            :result:
                (int) returns a list of tuples containing two integers (int, int) that is, 
                the ids of the contracts and payslips. 
        """
        if salary_struct_ids:
            condition = ','.join([f'{repr(s)}' for s in salary_struct_ids])
            condition = f'AND slip.struct_id IN ({condition})'
        else:
            condition = f''

        query = """
            	SELECT DISTINCT ON (contract.id)
                    contract.id
                FROM hr_payslip AS slip 
                    JOIN hr_contract AS contract ON slip.contract_id = contract.id
                WHERE
                    slip.is_holiday_nomina IS TRUE
                    AND (contract.date_end IS NULL OR (contract.date_end <= '{d_to}' AND '{d_from}' <= contract.date_end))
                    AND slip.state IN ('done', 'paid')
                    {cond}
                UNION
                SELECT DISTINCT ON (contract.id)
                    contract.id
                FROM hr_payslip AS slip
                    JOIN hr_contract AS contract ON slip.contract_id = contract.id
                WHERE
                    slip.is_holiday_nomina IS NOT TRUE
                    AND '{d_from}' <= slip.date_from AND slip.date_to <= '{d_to}'
                    AND (contract.date_end IS NULL OR (contract.date_end <= '{d_to}' AND '{d_from}' <= contract.date_end))
                    AND slip.state IN ('done', 'paid')
                    {cond}
        """.format(d_from=start_date, d_to=end_date, cond=condition)

        self._cr.execute(query)
        data = self.env.cr.fetchall()
        return data


    # Gets the contracts within the specified conditions and sends them to the banavih report view
    def print_banavih_report(self):
        registry_entries = self.env["wizard.report.banavih"]._get_banavih_contracts(self.start_date, self.end_date, self.salary_structure_type.ids)
        
        if registry_entries:
            contracts = [c[0] for c in registry_entries]
            self.contract_ids = self.contract_ids.browse(contracts)
            return self.env.ref('payslip_details_custom_itsales.banavih_report_action').report_action(self)
        else:
            raise MissingError(_('No se encontraron empleados para el tipo de nómina y estructura salarial en el periodo seleccionado.'))
    

    # Verity if the selected date is exactly within a month
    def _are_dates_in_month_limits(self, start_date, end_date):
        start_month = start_date.month
        end_month = end_date.month
        start_day = start_date.day
        end_day = end_date.day
        return start_month == end_month and start_day == 1 and end_day == calendar.monthrange(start_date.year, start_month)[1]


    # Adds a method to calculate the employee's accrued based on some rules, their current salary and vacations
    @api.model
    def _calculate_accrued_employee(self, employee, start_date, end_date):
        employee_on_holiday = False
        end_contract_date = employee.employee_id.contract_id.date_end
        ded  = employee._calculate_paid_interest_(start_date, end_date, ['DED', 'DED2'], True)
        accrued = employee._calculate_paid_interest_(start_date, end_date, ['BASIC', 'BASIC2', 'BASIC3', 'BASIC4',
                                                                            'PROM', 'PROMUTIL', 'UTIL'], True) - ded
        
        employee_on_holiday = employee._is_employee_on_holiday(start_date, end_date)
        
        # If the employee meets certain conditions, the accrued wage is rounded off 
        if not employee_on_holiday:
            if self._are_dates_in_month_limits(start_date, end_date):
                if not (end_contract_date and accrued == 0):
                    if accrued < employee.wage:
                        accrued = employee.wage
                    
        return accrued


    # Adds a validation check for the dates
    @api.constrains('start_date', 'end_date')
    def _check_valid_date_interval(self):
        if self.start_date > self.end_date :
            raise ValidationError(_('¡Error! La fecha de inicial debe ser anterior a la fecha final.'))


class HrContractCustomization(models.Model):
    _inherit = 'hr.contract'

    def _calculate_paid_interest_(self, start_date, end_date, codes, categ=False, limit=True):
        """
            This method finds the amount of salary rules or a complete category
            in a month that have the codes brang by parameter 'codes'

            :param:
                start_date: start date to search values of rules or categories
                end_date: end date to search values of rules or categories
                codes: a list of codes (must be string type)
                categ: a flag. If is true, the codes are for categories. Otherwise the codes are for rules

            :result:
                (float) the total amount of all codes converted to the fiscal currency
        """
        data = []
        if self.employee_id.id:
            codes = "', '".join(codes)
            if not categ:
                condition = "AND line.code IN ('{codes}')".format(codes=codes)            
            else:
                condition = "AND categ.code IN ('{codes}')".format(codes=codes)

            lim = "date_to" if limit else "date_from"

            """
                The first query is sums up those employees that have a holiday receipt within the specified month.
                The second query sums up the employee's regular receipts.
            """
            query = """
                SELECT
                    DISTINCT (struct_type.currency_id),
                    SUM(line.total) AS total
                FROM hr_payslip_line AS line
                    JOIN hr_payslip AS slip ON line.slip_id = slip.id
                    JOIN hr_salary_rule_category AS categ ON line.category_id = categ.id
                    JOIN hr_payroll_structure AS struct ON slip.struct_id = struct.id
                    JOIN hr_payroll_structure_type AS struct_type ON struct.type_id = struct_type.id
                WHERE
                    slip.employee_id = {id}
                    AND slip.is_holiday_nomina IS TRUE
                    {cond}
                    AND slip.state IN ('done', 'paid')
                    AND '{d_to}' <= slip.date_from AND slip.date_from <= '{d_from}'
                    AND slip.date_to BETWEEN '{d_from}' AND '{d_to}'
                GROUP BY
                    struct_type.currency_id
                UNION
                SELECT
                    DISTINCT(struct_type.currency_id),
                    SUM(line.total) AS total
                FROM hr_payslip_line AS line 
                    JOIN hr_payslip AS slip ON line.slip_id = slip.id
                    JOIN hr_salary_rule_category AS categ ON line.category_id = categ.id
                    JOIN hr_payroll_structure AS struct ON slip.struct_id = struct.id
                    JOIN hr_payroll_structure_type AS struct_type ON struct.type_id = struct_type.id
                WHERE
                    slip.employee_id = {id}
                    AND slip.is_holiday_nomina IS NOT TRUE
                    {cond}
                    AND slip.state IN ('done', 'paid')
                    AND '{d_from}' <= slip.date_from AND slip.{limit} <= '{d_to}'
                GROUP BY
                    struct_type.currency_id
            """.format(id=self.employee_id.id, cond=condition, d_from=start_date, d_to=end_date, limit=lim)
            self._cr.execute(query)
            data = self.env.cr.dictfetchall()
        return self._convert_to_fiscal(data)


    # Helper function to determine if a employee is on holiday
    def _is_employee_on_holiday(self, start_date, end_date):
        data = []
        vacation = False
        if self.employee_id.id:
            query="""
                SELECT 
                    DISTINCT (struct_type.currency_id),
                    0 AS total,
                    slip.is_holiday_nomina
                FROM hr_payslip_line AS line
                    JOIN hr_payslip AS slip ON line.slip_id = slip.id
                    JOIN hr_salary_rule_category AS categ ON line.category_id = categ.id
                    JOIN hr_payroll_structure AS struct ON slip.struct_id = struct.id
                    JOIN hr_payroll_structure_type AS struct_type ON struct.type_id = struct_type.id
                WHERE
                    slip.employee_id = {id}
                    AND slip.is_holiday_nomina IS TRUE
                    AND slip.state IN ('done', 'paid')
                    AND slip.date_to BETWEEN '{d_from}' AND '{d_to}'
                GROUP BY
                    struct_type.currency_id, slip.is_holiday_nomina
            """.format(id=self.employee_id.id, d_from=start_date, d_to=end_date)
            self._cr.execute(query)
            data = self.env.cr.dictfetchall()

            for reg in data:
                if reg.get('is_holiday_nomina', False):
                    vacation = True

            return vacation